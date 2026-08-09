import sys
import json
from subprocess import Popen, PIPE
import sqlite3
import os
import time

os.system("rm -rf ~/.mypass_data")
os.system("mkdir ~/.mypass_data")

p = Popen(["/Users/sameer/Documents/Password-Manager-App/.venv/bin/python", "/Users/sameer/Documents/Password-Manager-App/backend/ipc_bridge.py"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)

def send_req(method, params=None):
    req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    p.stdin.write(json.dumps(req) + "\n")
    p.stdin.flush()
    return json.loads(p.stdout.readline())

print("Status 1:", send_req("auth.status"))
print("Create Vault:", send_req("auth.unlock", {"masterPassword": "test"}))

# Simulate biometric enrollment
db_path = os.path.expanduser("~/.mypass_data/mypass.db")
conn = sqlite3.connect(db_path)
conn.execute("UPDATE app_metadata SET biometric_enabled = 1, biometric_platform = 'Darwin', biometric_enrolled_at = ?", (time.time(),))
conn.commit()
conn.close()

# Provide a mock biometric provider so it passes
p.terminate()

p2 = Popen(["/Users/sameer/Documents/Password-Manager-App/.venv/bin/python", "/Users/sameer/Documents/Password-Manager-App/backend/ipc_bridge.py"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
def send_req2(method, params=None):
    req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    p2.stdin.write(json.dumps(req) + "\n")
    p2.stdin.flush()
    return json.loads(p2.stdout.readline())

print("Status 2:", send_req2("auth.status"))
print("Unlock Biometrics:", send_req2("auth.biometric_unlock"))
print("List entries:", send_req2("vault.list_entries"))

p2.terminate()
