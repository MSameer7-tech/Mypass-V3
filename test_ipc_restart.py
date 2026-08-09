import sys
import json
from subprocess import Popen, PIPE

p = Popen(["/Users/sameer/Documents/Password-Manager-App/.venv/bin/python", "/Users/sameer/Documents/Password-Manager-App/backend/ipc_bridge.py"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)

def send_req(method, params=None):
    req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    p.stdin.write(json.dumps(req) + "\n")
    p.stdin.flush()
    res = p.stdout.readline()
    if not res:
        print("STDERR:", p.stderr.read())
    return res

print("Status 1:", send_req("auth.status"))
print("Unlock Vault:", send_req("auth.unlock", {"masterPassword": "test"}))
print("Status 2:", send_req("auth.status"))
print("List entries:", send_req("vault.list_entries"))

p.terminate()
