import sys
import json
from subprocess import Popen, PIPE

p = Popen(["python3", "/Users/sameer/Documents/Password-Manager-App/backend/ipc_bridge.py"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)

def send_req(method, params=None):
    req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    p.stdin.write(json.dumps(req) + "\n")
    p.stdin.flush()
    return p.stdout.readline()

print("Status 1:", send_req("auth.status"))
print("Stderr:", p.stderr.read())
