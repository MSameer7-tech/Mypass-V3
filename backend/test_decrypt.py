import json, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import ast

with open("/tmp/mypass_import_payload.txt", "r") as f:
    payload_str = f.read()

payload = json.loads(payload_str)
nonce = base64.b64decode(payload["nonce"].encode())
ciphertext = base64.b64decode(payload["ciphertext"].encode())

with open("/tmp/mypass_import_key.txt", "r") as f:
    key_str = f.read().strip()
    
# Convert b"..." string to actual bytes
key_bytes = ast.literal_eval(key_str)

try:
    plaintext = AESGCM(key_bytes).decrypt(nonce, ciphertext, None)
    print("SUCCESS")
except Exception as e:
    print("FAILED", type(e))
