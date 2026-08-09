import unittest
import json
import sqlite3
import subprocess
import os
import sys

class TestDBResilience(unittest.TestCase):
    def setUp(self):
        # We need a dummy DB file
        self.db_dir = "/tmp/mypass_test_db"
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_file = os.path.join(self.db_dir, "mypass.db")
        
        # Corrupt it by writing garbage
        with open(self.db_file, 'wb') as f:
            f.write(b'GARBAGE DATA' * 1000)
            
        # We have to patch build_data_path in a live subprocess, or just mock it.
        # It's easier to mock build_data_path in the actual python script using unittest.mock if we run it directly.
        pass

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_ipc_db_corruption_handling(self):
        # Let's run ipc_bridge.py directly but mock the DB path via env var or monkeypatch
        # We can write a quick wrapper script to inject the mock.
        wrapper = f"""
import sys
import os
sys.path.insert(0, '{os.path.abspath(".")}')
import ipc_bridge
ipc_bridge.build_data_path = lambda x: '{self.db_dir}'

ipc_bridge.main()
"""
        with open('/tmp/test_ipc_wrapper.py', 'w') as f:
            f.write(wrapper)
            
        # Run it and feed it a ping
        proc = subprocess.Popen(
            [sys.executable, '/tmp/test_ipc_wrapper.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "auth.status", "params": {}})
        stdout, stderr = proc.communicate(input=req + '\n')
        
        if not stdout.strip():
            self.fail(f"No stdout. Stderr: {stderr}")
            
        res = json.loads(stdout.strip())
        
        # Should return DB_ERROR
        self.assertFalse(res["result"]["success"])
        if res["result"]["error"]["code"] != "DB_ERROR":
            self.fail(f"Expected DB_ERROR but got: {res}\nStderr: {stderr}")
        self.assertIn("corrupted", res["result"]["error"]["message"])
        
if __name__ == '__main__':
    unittest.main()
