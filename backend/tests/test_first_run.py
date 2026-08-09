import os
import tempfile
import unittest
import json
import subprocess
import time

class TestFirstRun(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["MYPASS_DATA_DIR"] = self.temp_dir.name
        
        # Start the IPC bridge
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

    def tearDown(self):
        self.process.terminate()
        self.process.wait()
        self.temp_dir.cleanup()
        
    def _send_request(self, method, params=None):
        req = {"id": 1, "method": method, "params": params or {}}
        self.process.stdin.write(json.dumps(req) + "\n")
        self.process.stdin.flush()
        
        # Read response
        line = self.process.stdout.readline()
        if not line:
            return None
        return json.loads(line)

    def test_clean_installation(self):
        # 1. Clean Boot: Check Vault Status
        res = self._send_request("auth.status")
        self.assertIsNotNone(res)
        self.assertTrue(res["result"]["success"])
        # Should be NO_VAULT
        self.assertEqual(res["result"]["data"]["sessionState"], "NO_VAULT")
        
        # Verify db wasn't accidentally created with old legacy files
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir.name, "vault.key")))
        
        # 2. Vault Creation
        res = self._send_request("auth.unlock", {"masterPassword": "StrongPassword123!"})
        if not res["result"]["success"]:
            print(f"Error during unlock: {res['result'].get('error')}")
            err_line = self.process.stderr.readline()
            print(f"Stderr: {err_line}")
        self.assertTrue(res["result"]["success"])
        self.assertTrue(res["result"]["data"]["success"])
        
        # 3. DB Initialization
        # Verify the database exists
        db_path = os.path.join(self.temp_dir.name, ".mypass_data", "mypass.db")
        self.assertTrue(os.path.exists(db_path))
        
        # Check vault is unlocked
        res = self._send_request("auth.status")
        self.assertEqual(res["result"]["data"]["sessionState"], "UNLOCKED")

if __name__ == "__main__":
    unittest.main()
