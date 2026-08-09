import os
import tempfile
import unittest
import json
import subprocess

class TestUserJourney(unittest.TestCase):
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
        self._send_request("auth.unlock", {"masterPassword": "UserJourney123!"})

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

    def test_vault_lifecycle(self):
        # Already unlocked in setUp
        res = self._send_request("auth.status")
        self.assertEqual(res["result"]["data"]["sessionState"], "UNLOCKED")
        
        # Lock
        res = self._send_request("auth.lock")
        self.assertTrue(res["result"]["success"])
        
        # Status should be LOCKED
        res = self._send_request("auth.status")
        self.assertEqual(res["result"]["data"]["sessionState"], "LOCKED")
        
        # Unlock
        res = self._send_request("auth.unlock", {"masterPassword": "UserJourney123!"})
        self.assertTrue(res["result"]["success"])

    def test_crud_password(self):
        # Create
        res = self._send_request("vault.create_entry", {
            "title": "MyBank",
            "username": "user@bank.com",
            "password": "BankPassword!",
            "category": "Passwords"
        })
        self.assertTrue(res["result"]["success"])
        entry_id = res["result"]["data"]["id"]
        
        # Read
        res = self._send_request("vault.list_entries")
        if not res["result"].get("success"):
            print("ERROR IN GET_ENTRIES:", res)
        entries = res["result"]["data"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "MyBank")
        
        # Update
        res = self._send_request("vault.update_entry", {
            "id": entry_id,
            "title": "MyBank Updated"
        })
        self.assertTrue(res["result"]["success"])
        
        # Verify Update
        res = self._send_request("vault.list_entries")
        self.assertEqual(res["result"]["data"][0]["title"], "MyBank Updated")
        
        # Delete
        res = self._send_request("vault.delete_entry", {"id": entry_id})
        self.assertTrue(res["result"]["success"])
        
        res = self._send_request("vault.list_entries")
        self.assertEqual(len(res["result"]["data"]), 0)

    def test_crud_secure_note(self):
        res = self._send_request("vault.create_entry", {
            "title": "Secret Identity",
            "notes": "Batman is Bruce Wayne",
            "category": "Secure Notes"
        })
        self.assertTrue(res["result"]["success"])
        entry_id = res["result"]["data"]["id"]
        
        res = self._send_request("vault.update_entry", {
            "id": entry_id,
            "notes": "Superman is Clark Kent"
        })
        self.assertTrue(res["result"]["success"])
        
        res = self._send_request("vault.list_entries")
        self.assertEqual(res["result"]["data"][0]["notes"], "Superman is Clark Kent")
        
    def test_favorites(self):
        res = self._send_request("vault.create_entry", {
            "title": "FavApp",
            "category": "Passwords",
            "favorite": False
        })
        entry_id = res["result"]["data"]["id"]
        
        res = self._send_request("vault.toggle_favorite", {"id": entry_id})
        self.assertTrue(res["result"]["success"])
        
        res = self._send_request("vault.list_entries")
        self.assertTrue(res["result"]["data"][0]["is_favorite"])
        
        # Toggle back
        self._send_request("vault.toggle_favorite", {"id": entry_id})
        res = self._send_request("vault.list_entries")
        self.assertFalse(res["result"]["data"][0]["is_favorite"])

if __name__ == "__main__":
    unittest.main()
