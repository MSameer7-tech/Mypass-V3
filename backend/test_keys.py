import os
import base64
from crypto.key_derivation import Argon2KeyDerivationService
master_password = "BackupPassword123!"
kdf = Argon2KeyDerivationService()
parameters = kdf.default_parameters()
salt = b"mypass_backup_static_salt_v1_000"
key1 = kdf.derive_key(master_password, salt, parameters)
key2 = kdf.derive_key(master_password, salt, parameters)
print("Keys equal?", key1 == key2)
