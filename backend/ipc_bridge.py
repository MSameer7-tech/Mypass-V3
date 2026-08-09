#!/usr/bin/env python3
import sys
import json
import os

# Ensure backend directory is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import MasterPasswordService
from services.authentication_service import AuthenticationService
from services.vault_service import VaultService, EncryptionAdapter
from services.password_generator import PasswordGenerator, PasswordGeneratorOptions
from services.backup_service import BackupService
from utils.helpers import build_data_path

# Removed PassthroughEncryption

def validate_entry_payload(params: dict) -> None:
    title = params.get("title")
    if title is not None:
        if not isinstance(title, str) or len(title) == 0 or len(title) > 100:
            raise ValueError("Invalid title")
    
    for field, max_len in [("username", 100), ("password", 1024), ("website_url", 500), ("notes", 5000), ("category", 50)]:
        val = params.get(field)
        if val is not None and (not isinstance(val, str) or len(val) > max_len):
            raise ValueError(f"Invalid {field}")
            
    fav = params.get("favorite")
    if fav is not None and not isinstance(fav, bool):
        raise ValueError("Invalid favorite")



def main():
  db_dir = build_data_path(".mypass_data")
  os.makedirs(db_dir, exist_ok=True)
  db_file = os.path.join(db_dir, "mypass.db")
  
  import logging
  logging.basicConfig(filename=os.path.join(db_dir, 'ipc.log'), level=logging.DEBUG, format='%(asctime)s %(message)s')
  logging.info("Starting IPC bridge")

  import sqlite3
  db_error = None
  db_manager = None
  repo = None
  master_pwd_service = None
  auth_service = None

  try:
      db_manager = DatabaseManager(db_file)
      repo = VaultRepository(db_manager)
      master_pwd_service = MasterPasswordService(repo)
      auth_service = AuthenticationService(repo)
  except sqlite3.DatabaseError as e:
      db_error = "Database is corrupted or malformed."
  except sqlite3.OperationalError as e:
      db_error = "Database is locked or inaccessible."
  except Exception as e:
      db_error = "Failed to initialize database."
  vault_service = None
  generator = PasswordGenerator()
  backup_service = BackupService()


  while True:
    try:
      line = sys.stdin.readline()
      if not line:
        logging.info("EOF received, exiting.")
        break

      request = json.loads(line.strip())
      req_id = request.get("id")
      method = request.get("method")
      params = request.get("params", {})
      
      logging.info(f"Received request: {method} id={req_id}")

      if db_error:
        # If DB couldn't be loaded, we can't do anything else.
        if method == "system.ping":
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"status": "ok", "version": "1.0"}}}
        else:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "DB_ERROR", "message": db_error}}}
        print(json.dumps(response), flush=True)
        continue

      if method == "system.ping":
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"status": "ok", "version": "1.0"}}}

      elif method == "auth.status":
        metadata = repo.get_metadata()
        if vault_service:
            state = "UNLOCKED"
        elif not metadata.salt:
            state = "NO_VAULT"
        else:
            state = "LOCKED"
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"sessionState": state}}}

      elif method == "auth.unlock":
        master_password = params.get("masterPassword", "")
        # Note: Python `del` removes the reference but does not guarantee secure 
        # memory zeroization due to string immutability and GC behavior. 
        # However, we release the reference as quickly as possible.
        is_valid = bool(master_password and len(master_password) >= 1)
        if "masterPassword" in params:
          del params["masterPassword"]

        if is_valid:
          try:
            vault_service = master_pwd_service.create_vault_service(master_password)
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}
          except Exception as e:
            logging.error(f"Error unlocking vault: {e}", exc_info=True)
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_INVALID_PASSWORD", "message": str(e)}}}
          finally:
            del master_password
        else:
          response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_INVALID_PASSWORD", "message": "Invalid master password."}}}

      elif method == "auth.lock":
        vault_service = None
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "auth.biometric_unlock":
        if not auth_service.is_biometric_enabled():
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_BIOMETRIC_DISABLED", "message": "Touch ID / Biometrics is not enabled in Settings."}}}
        else:
            vs = auth_service.unlock_vault_with_biometrics("Unlock MyPass Vault")
            if vs is not None:
                vault_service = vs
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}
            else:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_BIOMETRIC_FAILED", "message": "Biometric authentication failed or canceled."}}}

      elif method == "auth.biometric_status":
        available = auth_service.is_biometric_available()
        enabled = auth_service.is_biometric_enabled()
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"available": available, "enabled": enabled}}}

      elif method == "auth.enable_biometrics":
        if vault_service is None:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Vault is locked."}}}
        else:
            success = auth_service.setup_biometrics("Enable Touch ID for MyPass", vault_service)
            if success:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}
            else:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_BIOMETRIC_FAILED", "message": "Failed to configure biometrics. Canceled or unavailable."}}}

      elif method == "auth.disable_biometrics":
        auth_service.disable_biometrics()
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "vault.list_entries":
        if vault_service is None:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Vault is locked."}}}
            print(json.dumps(response), flush=True)
            continue
        entries = vault_service.list_all_entries()
        dtos = []
        for e in entries:
          dtos.append({
            "id": e.id,
            "title": e.title,
            "username": e.username,
            "password": e.password,
            "website_url": getattr(e, "website", getattr(e, "website_url", "")),
            "notes": e.notes,
            "is_favorite": getattr(e, "favorite", False),
            "category": getattr(e, "category", "Passwords") or "Passwords",
            "updated_at": getattr(e, "updated_at", ""),
            "created_at": getattr(e, "created_at", ""),
          })
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": dtos}}

      elif method == "vault.create_entry":
        if vault_service is None:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Vault is locked."}}}
            print(json.dumps(response), flush=True)
            continue
        try:
            validate_entry_payload(params)
            if not params.get("title"):
                raise ValueError("Title is required for creation")
        except ValueError as e:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}}
            print(json.dumps(response), flush=True)
            continue

        title = params.get("title", "New Entry")
        username = params.get("username", "")
        password = params.get("password", "")
        website_url = params.get("website_url", "")
        notes = params.get("notes", "")
        category = params.get("category", "")
        favorite = params.get("favorite", False)

        record = vault_service.save_entry(
            title=title, website=website_url, username=username, password=password, notes=notes,
            category=category, favorite=favorite
        )
        
        if "password" in params:
          del params["password"]
        del password

        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"id": record.id, "title": record.title}}}

      elif method == "vault.update_entry":
        if vault_service is None:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Vault is locked."}}}
            print(json.dumps(response), flush=True)
            continue
        try:
            validate_entry_payload(params)
            entry_id = params.get("id")
            if not isinstance(entry_id, int) or entry_id <= 0:
                raise ValueError("Invalid entry ID")
        except ValueError as e:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}}
            print(json.dumps(response), flush=True)
            continue

        entry_id = params.get("id")
        title = params.get("title")
        username = params.get("username")
        password = params.get("password")
        website_url = params.get("website_url")
        notes = params.get("notes")
        category = params.get("category")
        favorite = params.get("favorite")

        record = vault_service.get_entry(entry_id)
        if record:
          vault_service.save_entry(
            title=title if title is not None else record.title,
            website=website_url if website_url is not None else record.website,
            username=username if username is not None else record.username,
            password=password if password is not None else record.password,
            notes=notes if notes is not None else record.notes,
            category=category if category is not None else record.category,
            favorite=favorite if favorite is not None else record.favorite,
            entry_id=entry_id,
          )
          
        if "password" in params:
          del params["password"]
        del password

        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "vault.delete_entry":
        if vault_service is None:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Vault is locked."}}}
            print(json.dumps(response), flush=True)
            continue
        entry_id = params.get("id")
        vault_service.delete_entry(entry_id)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "vault.toggle_favorite":
        if vault_service is None:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Vault is locked."}}}
            print(json.dumps(response), flush=True)
            continue
        entry_id = params.get("id")
        record = vault_service.get_entry(entry_id)
        if record:
            vault_service.save_entry(
                title=record.title,
                website=record.website,
                username=record.username,
                password=record.password,
                notes=record.notes,
                category=record.category,
                favorite=not record.favorite,
                entry_id=entry_id,
            )
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "generator.generate":
        length = params.get("length", 16)
        include_symbols = params.get("symbols", True)
        include_numbers = params.get("numbers", True)
        opts = PasswordGeneratorOptions(length=length, symbols=include_symbols, numbers=include_numbers)
        pwd = generator.generate(opts)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"password": pwd}}}

      elif method == "backup.export":
        if vault_service is None:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Vault is locked."}}}
            print(json.dumps(response), flush=True)
            continue
            
        export_format = params.get("format", "mypass")
        entries = vault_service.list_all_entries()
        
        if export_format == "json":
            export_payload = json.dumps([{ "title": e.title, "username": e.username, "password": e.password, "website_url": e.website, "notes": e.notes, "category": e.category, "favorite": e.favorite } for e in entries], indent=2)
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"filename": "mypass-vault-backup.json", "payload": export_payload, "itemCount": len(entries)}}}
        else:
            # Encrypted .mypass backup using existing session key
            from dataclasses import asdict
            payload_dict = {
                "format_version": backup_service.format_version,
                "entries": [asdict(entry) for entry in entries],
                "history": [] # Simplified for Phase 11
            }
            raw_payload = json.dumps(payload_dict)
            encrypted_payload = vault_service.backup_encryption_service.encrypt(raw_payload)
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"filename": "mypass-vault-backup.mypass", "payload": encrypted_payload, "itemCount": len(entries)}}}

      elif method == "backup.import":
        if vault_service is None:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "Vault is locked."}}}
            print(json.dumps(response), flush=True)
            continue
        
        payload = params.get("payload", "")
        
        # Determine if payload is JSON or .mypass encrypted string
        is_encrypted = False
        try:
            parsed_initial = json.loads(payload)
            if isinstance(parsed_initial, dict) and "nonce" in parsed_initial and "ciphertext" in parsed_initial:
                is_encrypted = True
        except:
            pass

        if is_encrypted:
            try:
                decrypted_payload = vault_service.backup_encryption_service.decrypt(payload)
                parsed_payload = json.loads(decrypted_payload)
                if parsed_payload.get("format_version") != backup_service.format_version:
                    raise ValueError("Unsupported backup format.")
                items = parsed_payload.get("entries", [])
            except Exception as err:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Failed to decrypt or parse backup: " + repr(err)}}}
                print(json.dumps(response), flush=True)
                continue
        else:
            try:
                items = json.loads(payload)
                if not isinstance(items, list):
                    raise ValueError("Payload must be a JSON array of entries")
            except (json.JSONDecodeError, ValueError) as e:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}}
                print(json.dumps(response), flush=True)
                continue
            
        # Atomic Import: Validate everything first
        validated_items = []
        for index, item in enumerate(items):
            if isinstance(item, dict) and "title" in item:
                try:
                    validate_entry_payload(item)
                    validated_items.append(item)
                except ValueError as e:
                    # Fail the entire import if any entry is malformed (Atomic)
                    response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "VALIDATION_ERROR", "message": f"Malformed entry at index {index}: {str(e)}"}}}
                    break
            else:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "VALIDATION_ERROR", "message": f"Invalid entry format at index {index}"}}}
                break
        else:
            # If we didn't break, all items are valid. Insert them atomically.
            try:
                count = 0
                for item in validated_items:
                    vault_service.save_entry(
                        title=item.get("title", "Imported"), 
                        website=item.get("website_url", ""), 
                        username=item.get("username", ""), 
                        password=item.get("password", ""),
                        notes=item.get("notes", ""),
                        category=item.get("category", ""),
                        favorite=item.get("favorite", False)
                    )
                    count += 1
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"importedCount": count}}}
            except Exception as e:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}}


      else:
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "METHOD_NOT_FOUND", "message": f"Method {method} not found."}}}

      print(json.dumps(response), flush=True)

    except Exception as err:
      logging.error(f"Internal application error: {err}", exc_info=True)
      err_resp = {"jsonrpc": "2.0", "id": req_id if 'req_id' in locals() else None, "result": {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An internal application error occurred."}}}
      print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
  main()
