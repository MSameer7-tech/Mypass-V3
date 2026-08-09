import os
import shutil
import tempfile
import base64

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import MasterPasswordService
from crypto.key_derivation import Argon2KeyDerivationService

def test_keys():
    temp_dir = tempfile.TemporaryDirectory()
    
    # 1. Create first vault
    db_path1 = os.path.join(temp_dir.name, "vault1.db")
    repo1 = VaultRepository(DatabaseManager(db_path1))
    service1 = MasterPasswordService(repo1)
    vault1 = service1.create_vault_service("BackupPassword123!")
    key1 = vault1.backup_encryption_service.key
    
    # 2. Create second vault
    db_path2 = os.path.join(temp_dir.name, "vault2.db")
    repo2 = VaultRepository(DatabaseManager(db_path2))
    service2 = MasterPasswordService(repo2)
    vault2 = service2.create_vault_service("BackupPassword123!")
    key2 = vault2.backup_encryption_service.key
    
    print("Key 1:", key1)
    print("Key 2:", key2)
    print("Equal?", key1 == key2)
    
test_keys()
