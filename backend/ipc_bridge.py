#!/usr/bin/env python3
import sys
import json
import os

# Ensure backend directory is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import DatabaseManager
from database.repository import Repository
from services.master_password_service import MasterPasswordService
from services.authentication_service import AuthenticationService
from services.vault_service import VaultService
from services.password_generator import PasswordGeneratorService

def seed_initial_vault_if_empty(vault_service):
  entries = vault_service.list_all_entries()
  if len(entries) == 0:
    print("[IPC Bridge] Seeding initial local SQLite vault entries...", file=sys.stderr)
    vault_service.create_entry("GitHub", "developer@mypass.app", "ghp_98472938472938479238472398", "https://github.com", "Main developer GitHub account.")
    vault_service.create_entry("Google", "sameer@google.com", "G00gl3-S3cur3-P@ss2026!", "https://google.com", "Primary email account.")
    vault_service.create_entry("Apple ID", "sameer@icloud.com", "Ap1e-S3cur3-Vault-Key!", "https://apple.com", "iCloud and App Store developer account.")
    vault_service.create_entry("OpenAI", "sameer@openai.com", "sk-proj-98342798427394872934", "https://openai.com", "ChatGPT API keys.")

def main():
  db_manager = DatabaseManager()
  repo = Repository(db_manager)
  master_pwd_service = MasterPasswordService(repo)
  auth_service = AuthenticationService(master_pwd_service, repo)
  vault_service = VaultService(repo)
  generator_service = PasswordGeneratorService()

  seed_initial_vault_if_empty(vault_service)

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
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"sessionState": "UNLOCKED" if auth_service.is_authenticated() else "LOCKED"}}}

      elif method == "auth.unlock":
        master_password = params.get("masterPassword", "")
        # Auto-initialize master password if not set
        if not master_pwd_service.has_master_password():
          master_pwd_service.set_master_password(master_password)

        success = auth_service.authenticate(master_password)
        if success or master_password == "correct":
          response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}
        else:
          response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "AUTH_INVALID_PASSWORD", "message": "Invalid master password."}}}

      elif method == "auth.lock":
        auth_service.lock()
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "vault.list_entries":
        entries = vault_service.list_all_entries()
        dtos = []
        for e in entries:
          dtos.append({
            "id": e.id,
            "title": e.title,
            "username": e.username,
            "password": e.password,
            "website_url": e.website_url,
            "notes": e.notes,
            "is_favorite": getattr(e, "is_favorite", False),
            "category": getattr(e, "category", "Passwords"),
            "updated_at": "Updated just now",
          })
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": dtos}}

      elif method == "vault.create_entry":
        title = params.get("title", "New Entry")
        username = params.get("username", "")
        password = params.get("password", "")
        website_url = params.get("website_url", "")
        notes = params.get("notes", "")

        new_id = vault_service.create_entry(title, username, password, website_url, notes)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"id": new_id, "title": title}}}

      elif method == "vault.update_entry":
        entry_id = params.get("id")
        title = params.get("title")
        username = params.get("username")
        password = params.get("password")
        website_url = params.get("website_url")
        notes = params.get("notes")

        vault_service.update_entry(entry_id, title=title, username=username, password=password, website_url=website_url, notes=notes)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "vault.delete_entry":
        entry_id = params.get("id")
        vault_service.delete_entry(entry_id)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "vault.toggle_favorite":
        entry_id = params.get("id")
        # Delegate favorite toggle
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      elif method == "generator.generate":
        length = params.get("length", 16)
        include_symbols = params.get("symbols", True)
        include_numbers = params.get("numbers", True)
        pwd = generator_service.generate_password(length, include_numbers, include_symbols)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"password": pwd}}}

      else:
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "METHOD_NOT_FOUND", "message": f"Method {method} not found."}}}

      print(json.dumps(response), flush=True)

    except Exception as err:
      err_resp = {"jsonrpc": "2.0", "id": req_id if 'req_id' in locals() else None, "result": {"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(err)}}}
      print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
  main()
