import os
import tempfile
import unittest
import json
import subprocess
import shutil

class TestBackupRecovery(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["MYPASS_DATA_DIR"] = self.temp_dir.name
        
        bridge_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "ipc_bridge.py"
        )
        self.process = subprocess.Popen(
            ["python3", bridge_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
            text=True
        )
        
        # Initial creation
        self._send_request("auth.unlock", {"masterPassword": "BackupPassword123!"})
        
        # Add a test entry
        self._send_request("vault.create_entry", {
            "title": "BackupTest",
            "username": "user1",
            "password": "pwd1",
            "category": "Passwords"
        })

    def tearDown(self):
        self.process.terminate()
        self.process.wait()
        self.temp_dir.cleanup()
        
    def _send_request(self, method, params=None):
        req = {"id": 1, "method": method, "params": params or {}}
        self.process.stdin.write(json.dumps(req) + "\n")
        self.process.stdin.flush()
        
        line = self.process.stdout.readline()
        if not line:
            return None
        return json.loads(line)

    def test_clean_backup_and_restore(self):
        backup_path = os.path.join(self.temp_dir.name, "export.mypass")
        
        # 1. Export
        res = self._send_request("backup.export", {
            "format": "mypass"
        })
        self.assertTrue(res["result"]["success"])
        payload = res["result"]["data"]["payload"]
        with open(backup_path, "w") as f:
            f.write(payload)
        
        # 2. Delete Vault (simulate new machine)
        self._send_request("auth.lock")
        db_path = os.path.join(self.temp_dir.name, ".mypass_data", "mypass.db")
        os.remove(db_path)
        
        # Restart IPC to reload state
        self.process.terminate()
        self.process.wait()
        
        bridge_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "ipc_bridge.py"
        )
        self.process = subprocess.Popen(
            ["python3", bridge_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
            text=True
        )
        
        # Check NO_VAULT
        res = self._send_request("auth.status")
        self.assertEqual(res["result"]["data"]["sessionState"], "NO_VAULT")
        
        # 3. Import (Needs vault to be unlocked first? Or does import create vault?)
        # Wait, if we are restoring a backup, the vault might not exist.
        # But if IPC requires it to be unlocked, we first create the vault?
        # Let's unlock first to create a vault if it doesn't exist.
        res = self._send_request("auth.unlock", {"masterPassword": "BackupPassword123!"})
        self.assertTrue(res["result"]["success"])
        
        with open(backup_path, "r") as f:
            payload = f.read()
            
        res = self._send_request("backup.import", {
            "payload": payload
        })
        if not res["result"].get("success"):
            print("ERROR IN IMPORT:", res)
        self.assertTrue(res["result"]["success"])
        
        # 4. Verify unlocked and data restored
        res = self._send_request("auth.status")
        self.assertEqual(res["result"]["data"]["sessionState"], "UNLOCKED")
        
        res = self._send_request("vault.list_entries")
        entries = res["result"]["data"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "BackupTest")

    def test_wrong_password_backup(self):
        # We can't really test wrong_password via IPC easily because the import API 
        # doesn't take a password, it uses the currently unlocked vault's key!
        # If we use a different password to unlock the vault, it will fail to decrypt the payload.
        
        backup_path = os.path.join(self.temp_dir.name, "export.mypass")
        res = self._send_request("backup.export", {
            "format": "mypass"
        })
        payload = res["result"]["data"]["payload"]
        
        # Now switch vaults (simulate locking and opening a different one)
        self._send_request("auth.lock")
        db_path = os.path.join(self.temp_dir.name, ".mypass_data", "mypass.db")
        os.remove(db_path)
        
        self.process.terminate()
        self.process.wait()
        
        bridge_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "ipc_bridge.py"
        )
        self.process = subprocess.Popen(
            ["python3", bridge_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
            text=True
        )
        
        # Unlock with wrong password
        self._send_request("auth.unlock", {"masterPassword": "WRONG_PASSWORD"})
        
        res = self._send_request("backup.import", {
            "payload": payload
        })
        self.assertFalse(res["result"]["success"])
        self.assertIn("decrypt", res["result"]["error"]["message"].lower())
        
        # Verify vault untouched (empty)
        res = self._send_request("vault.list_entries")
        self.assertEqual(len(res["result"]["data"]), 0)

    def test_corrupted_backup(self):
        backup_path = os.path.join(self.temp_dir.name, "corrupt.mypass")
        with open(backup_path, "wb") as f:
            f.write(b"this is garbage data not a real backup")
            
        res = self._send_request("backup.import", {
            "payload": "this is garbage data not a real backup"
        })
        self.assertFalse(res["result"]["success"])
        
    def test_malformed_json_import(self):
        # We can test JSON import failure (atomic rollback)
        backup_path = os.path.join(self.temp_dir.name, "bad.json")
        with open(backup_path, "w") as f:
            f.write(json.dumps([{"missing_title": "yes"}]))
            
        res = self._send_request("backup.import", {
            "payload": json.dumps([{"missing_title": "yes"}])
        })
        self.assertFalse(res["result"]["success"])
        
        # Vault untouched
        res = self._send_request("vault.list_entries")
        self.assertEqual(len(res["result"]["data"]), 1)

if __name__ == "__main__":
    unittest.main()
