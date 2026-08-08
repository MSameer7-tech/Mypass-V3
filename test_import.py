import subprocess
import json
import sys

proc = subprocess.Popen(['/Users/sameer/Documents/Password-Manager-App/.venv/bin/python', 'backend/ipc_bridge.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

def send_request(method, params=None):
    req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    proc.stdin.write(json.dumps(req) + '\n')
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())

with open("user_json.json") as f:
    payload = f.read()

print("Import:", send_request("backup.import", {"payload": payload}))
print("List:", send_request("vault.list_entries"))
proc.terminate()
