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

def main():
  db_manager = DatabaseManager()
  repo = Repository(db_manager)
  master_pwd_service = MasterPasswordService(repo)
  auth_service = AuthenticationService(master_pwd_service, repo)
  vault_service = VaultService(repo)

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
        success = auth_service.authenticate(master_password)
        if success:
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
            "updated_at": "Just now",
          })
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": dtos}}

      elif method == "vault.delete_entry":
        entry_id = params.get("id")
        vault_service.delete_entry(entry_id)
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": True, "data": {"success": True}}}

      else:
        response = {"jsonrpc": "2.0", "id": req_id, "result": {"success": False, "error": {"code": "METHOD_NOT_FOUND", "message": f"Method {method} not found."}}}

      print(json.dumps(response), flush=True)

    except Exception as err:
      err_resp = {"jsonrpc": "2.0", "id": req_id if 'req_id' in locals() else None, "result": {"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(err)}}}
      print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
  main()
