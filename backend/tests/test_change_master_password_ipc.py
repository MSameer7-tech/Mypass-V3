import os
import unittest
import tempfile
import json
import subprocess
import sys

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import MasterPasswordService


class TestChangeMasterPasswordIPC(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_dir = os.path.join(self.test_dir.name, ".mypass_data")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, "mypass.db")
        
        # Initialize DB with known master password
        db_mgr = DatabaseManager(self.db_path)
        repo = VaultRepository(db_mgr)
        svc = MasterPasswordService(repo)
        vs = svc.create_vault_service("MasterPassword123!")
        vs.save_entry("Test Site", "https://test.com", "admin", "SecretPass123!", "Notes")

        # Launch ipc_bridge subprocess with MYPASS_DATA_DIR pointing to test_dir
        env = os.environ.copy()
        env["MYPASS_DATA_DIR"] = self.test_dir.name
        env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ipc_bridge.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

    def tearDown(self):
        self.proc.terminate()
        self.proc.wait()
        self.test_dir.cleanup()

    def _rpc(self, method: str, params: dict = None, req_id: int = 1) -> dict:
        req = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line.strip())

    def test_ipc_change_password_flow(self):
        # 1. Unlock with old password
        res = self._rpc("auth.unlock", {"masterPassword": "MasterPassword123!"}, 1)
        self.assertTrue(res["result"]["success"])

        # 2. Change password to new password
        res = self._rpc("auth.change_master_password", {
            "currentPassword": "MasterPassword123!",
            "newPassword": "NewMasterPassword456!",
        }, 2)
        self.assertTrue(res["result"]["success"])

        # 3. Status should now be LOCKED (session invalidated)
        res = self._rpc("auth.status", {}, 3)
        self.assertEqual(res["result"]["data"]["sessionState"], "LOCKED")

        # 4. Old password should fail
        res = self._rpc("auth.unlock", {"masterPassword": "MasterPassword123!"}, 4)
        self.assertFalse(res["result"]["success"])
        self.assertEqual(res["result"]["error"]["code"], "AUTH_INVALID_PASSWORD")

        # 5. New password should succeed
        res = self._rpc("auth.unlock", {"masterPassword": "NewMasterPassword456!"}, 5)
        self.assertTrue(res["result"]["success"])

        # 6. Verify entry decrypts correctly
        res = self._rpc("vault.list_entries", {}, 6)
        entries = res["result"]["data"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "Test Site")
        self.assertEqual(entries[0]["password"], "SecretPass123!")

    def test_ipc_change_password_validation_errors(self):
        # Unlock
        self._rpc("auth.unlock", {"masterPassword": "MasterPassword123!"}, 1)

        # Same password
        res = self._rpc("auth.change_master_password", {
            "currentPassword": "MasterPassword123!",
            "newPassword": "MasterPassword123!",
        }, 2)
        self.assertFalse(res["result"]["success"])
        self.assertEqual(res["result"]["error"]["code"], "AUTH_SAME_PASSWORD")

        # Short password
        res = self._rpc("auth.change_master_password", {
            "currentPassword": "MasterPassword123!",
            "newPassword": "short",
        }, 3)
        self.assertFalse(res["result"]["success"])
        self.assertEqual(res["result"]["error"]["code"], "AUTH_INVALID_LENGTH")

        # Wrong current password
        res = self._rpc("auth.change_master_password", {
            "currentPassword": "WrongCurrentPassword99!",
            "newPassword": "ValidNewPassword456!",
        }, 4)
        self.assertFalse(res["result"]["success"])
        self.assertEqual(res["result"]["error"]["code"], "AUTH_INVALID_PASSWORD")


if __name__ == "__main__":
    unittest.main()
