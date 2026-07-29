import json
from dataclasses import asdict
from pathlib import Path

from database.models import PasswordHistoryRecord, VaultEntryRecord


class BackupService:
    format_version = 1

    def create_backup(self, vault_service, backup_path: str) -> None:
        entries = vault_service.list_all_entries()
        history = [
            item
            for entry in entries
            for item in vault_service.get_password_history(entry.id)
        ]
        payload = json.dumps(
            {
                "format_version": self.format_version,
                "entries": [asdict(entry) for entry in entries],
                "history": [asdict(item) for item in history],
            }
        )
        encrypted_payload = vault_service.encryption_service.encrypt(payload)
        Path(backup_path).write_text(encrypted_payload, encoding="utf-8")

    def restore_backup(self, vault_service, backup_path: str) -> None:
        encrypted_payload = Path(backup_path).read_text(encoding="utf-8")
        payload = json.loads(vault_service.encryption_service.decrypt(encrypted_payload))
        if payload.get("format_version") != self.format_version:
            raise ValueError("Unsupported backup format.")
        entries = [VaultEntryRecord(**entry) for entry in payload.get("entries", [])]
        history = [PasswordHistoryRecord(**item) for item in payload.get("history", [])]
        vault_service.replace_vault_contents(entries, history)
