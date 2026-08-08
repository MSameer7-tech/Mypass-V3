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

class PassthroughEncryption(EncryptionAdapter):
  def encrypt(self, value: str) -> str:
    return value or ""
  def decrypt(self, value: str) -> str:
    return value or ""



def main():
  db_dir = build_data_path(".mypass_data")
  os.makedirs(db_dir, exist_ok=True)
  db_file = os.path.join(db_dir, "mypass.db")

  db_manager = DatabaseManager(db_file)
  repo = VaultRepository(db_manager)
  encryption = PassthroughEncryption()
  master_pwd_service = MasterPasswordService(repo)
  auth_service = AuthenticationService(repo)
  vault_service = VaultService(repo, encryption)
  generator = PasswordGenerator()
  backup_service = BackupService()


  while True:
    try:
      line = sys.stdin.readline()
      if not line:
        break

      request = json.loads(line.strip())
      req_id = request.get("id")
      method = request.get("method")
      params = request.get("params", {})

      if method == "system.ping":
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"status": "ok", "version": "1.0"}}}

      elif method == "auth.status":
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"sessionState": "LOCKED"}}}

      elif method == "auth.unlock":
        master_password = params.get("masterPassword", "")
        if master_password and len(master_password) >= 1:
          response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}
        else:
          response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_INVALID_PASSWORD", "message": "Invalid master password."}}}

      elif method == "auth.lock":
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "auth.biometric_unlock":
        if auth_service.is_biometric_available():
          if auth_service._provider.authenticate_user("Unlock MyPass Vault"):
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}
          else:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_BIOMETRIC_FAILED", "message": "Biometric authentication failed or canceled."}}}
        else:
          response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_BIOMETRIC_UNAVAILABLE", "message": "Biometrics not available on this device."}}}


      elif method == "vault.list_entries":
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
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"id": record.id, "title": record.title}}}

      elif method == "vault.update_entry":
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
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "vault.delete_entry":
        entry_id = params.get("id")
        vault_service.delete_entry(entry_id)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "vault.toggle_favorite":
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
        entries = vault_service.list_all_entries()
        export_payload = json.dumps([{ "title": e.title, "username": e.username, "password": e.password, "website_url": e.website } for e in entries], indent=2)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"filename": "mypass-vault-backup.json", "payload": export_payload, "itemCount": len(entries)}}}

      elif method == "backup.import":
        payload = params.get("payload", "[]")
        items = json.loads(payload)
        count = 0
        for item in items:
          if isinstance(item, dict) and "title" in item:
            vault_service.save_entry(title=item.get("title", "Imported"), website=item.get("website_url", ""), username=item.get("username", ""), password=item.get("password", ""))
            count += 1
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"importedCount": count}}}

      else:
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "METHOD_NOT_FOUND", "message": f"Method {method} not found."}}}

      print(json.dumps(response), flush=True)

    except Exception as err:
      err_resp = {"jsonrpc": "2.0", "id": req_id if 'req_id' in locals() else None, "result": {"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(err)}}}
      print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
  main()
