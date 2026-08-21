from typing import Optional

from database.database import DatabaseManager
from database.models import AppMetadataRecord, PasswordHistoryRecord, VaultEntryRecord
from datetime import datetime, UTC


class VaultRepository:
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    def count_entries(self) -> int:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT count(*) FROM vault_entries")
            return cursor.fetchone()[0]

    def get_metadata(self) -> AppMetadataRecord:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT version, created, vault_id, argon_parameters, salt, 
                       biometric_enabled, biometric_platform, biometric_enrolled_at,
                       biometric_prompt_state, last_master_password_change, biometric_wrapped_key
                FROM app_metadata
                WHERE id = 1
                """
            )
            row = cursor.fetchone()
            return AppMetadataRecord(
                version=row[0],
                created=row[1],
                vault_id=row[2],
                argon_parameters=row[3],
                salt=row[4],
                biometric_enabled=bool(row[5]),
                biometric_platform=row[6],
                biometric_enrolled_at=row[7],
                biometric_prompt_state=row[8],
                last_master_password_change=row[9],
                biometric_wrapped_key=row[10],
            )

    def update_metadata_security(
        self,
        *,
        version: str,
        vault_id: str,
        argon_parameters: str,
        salt: str,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE app_metadata
                SET version = ?, vault_id = ?, argon_parameters = ?, salt = ?
                WHERE id = 1
                """,
                (version, vault_id, argon_parameters, salt),
            )

    def update_biometric_metadata(
        self,
        *,
        enabled: bool,
        platform: str | None = None,
        enrolled_at: float | None = None,
        wrapped_key: str | None = None,
    ) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE app_metadata
                SET biometric_enabled = ?, biometric_platform = ?, biometric_enrolled_at = ?, biometric_wrapped_key = ?
                WHERE id = 1
                """,
                (int(enabled), platform, enrolled_at, wrapped_key),
            )

    def update_vault_crypto_transaction(self, version, vault_id, argon_parameters, salt, encrypted_entries_data, encrypted_history_data) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            # 1. Update metadata including resetting biometric wrapper
            cursor.execute(
                """
                UPDATE app_metadata
                SET version = ?, vault_id = ?, argon_parameters = ?, salt = ?, last_master_password_change = ?,
                    biometric_enabled = 0, biometric_platform = NULL, biometric_enrolled_at = NULL, biometric_wrapped_key = NULL
                WHERE id = 1
                """,
                (version, vault_id, argon_parameters, salt, self._timestamp()),
            )
            
            # 2. Update entries
            for entry_id, new_password, new_notes, updated_at in encrypted_entries_data:
                cursor.execute(
                    "UPDATE vault_entries SET password = ?, notes = ?, updated_at = ? WHERE id = ?",
                    (new_password, new_notes, updated_at, entry_id),
                )
                
            # 3. Update history
            for history_id, new_password in encrypted_history_data:
                cursor.execute(
                    "UPDATE password_history SET password = ? WHERE id = ?",
                    (new_password, history_id),
                )

    def update_biometric_prompt_state(self, state: str) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE app_metadata SET biometric_prompt_state = ? WHERE id = 1",
                (state,),
            )

    def update_last_master_password_change(self) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE app_metadata SET last_master_password_change = ? WHERE id = 1",
                (self._timestamp(),),
            )

    def get_entry_by_id(self, entry_id: int) -> Optional[VaultEntryRecord]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, title, website, username, password, notes, category, tags, icon, favorite,
                       created_at, updated_at
                FROM vault_entries
                WHERE id = ?
                """,
                (entry_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def get_latest_entry_by_website(self, website: str) -> Optional[VaultEntryRecord]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, title, website, username, password, notes, category, tags, icon, favorite,
                       created_at, updated_at
                FROM vault_entries
                WHERE website = ?
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
                """,
                (website,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def list_entries_by_website(self, website: str) -> list[VaultEntryRecord]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, title, website, username, password, notes, category, tags, icon, favorite,
                       created_at, updated_at
                FROM vault_entries
                WHERE website = ?
                ORDER BY updated_at DESC, id DESC
                """,
                (website,),
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def list_all_entries(self) -> list[VaultEntryRecord]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, title, website, username, password, notes, category, tags, icon, favorite,
                       created_at, updated_at
                FROM vault_entries
                ORDER BY id ASC
                """
            )
            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def create_entry(self, entry: VaultEntryRecord) -> VaultEntryRecord:
        timestamp = self._timestamp()
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO vault_entries (
                    title, website, username, password, notes, category, tags, icon, favorite,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.title,
                    entry.website,
                    entry.username,
                    entry.password,
                    entry.notes,
                    entry.category,
                    entry.tags,
                    entry.icon,
                    int(entry.favorite),
                    timestamp,
                    timestamp,
                ),
            )
            return VaultEntryRecord(
                id=cursor.lastrowid,
                title=entry.title,
                website=entry.website,
                username=entry.username,
                password=entry.password,
                notes=entry.notes,
                category=entry.category,
                tags=entry.tags,
                icon=entry.icon,
                favorite=entry.favorite,
                created_at=timestamp,
                updated_at=timestamp,
            )

    def update_entry(self, entry: VaultEntryRecord) -> VaultEntryRecord:
        if entry.id is None:
            raise ValueError("Entry id is required for updates")

        updated_at = self._timestamp()
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE vault_entries
                SET title = ?, website = ?, username = ?, password = ?, notes = ?,
                    category = ?, tags = ?, icon = ?, favorite = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    entry.title,
                    entry.website,
                    entry.username,
                    entry.password,
                    entry.notes,
                    entry.category,
                    entry.tags,
                    entry.icon,
                    int(entry.favorite),
                    updated_at,
                    entry.id,
                ),
            )
        return VaultEntryRecord(
            id=entry.id,
            title=entry.title,
            website=entry.website,
            username=entry.username,
            password=entry.password,
            notes=entry.notes,
            category=entry.category,
            tags=entry.tags,
            icon=entry.icon,
            favorite=entry.favorite,
            created_at=entry.created_at,
            updated_at=updated_at,
        )

    def update_entry_password(self, entry_id: int, password: str) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE vault_entries
                SET password = ?, updated_at = ?
                WHERE id = ?
                """,
                (password, self._timestamp(), entry_id),
            )

    def update_entry_notes(self, entry_id: int, notes: str) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE vault_entries SET notes = ?, updated_at = ? WHERE id = ?",
                (notes, self._timestamp(), entry_id),
            )

    def delete_entry_by_id(self, entry_id: int) -> None:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM password_history WHERE entry_id = ?", (entry_id,))
            cursor.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,))

    def add_password_history(self, entry_id: int, password: str) -> PasswordHistoryRecord:
        created_at = self._timestamp()
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO password_history (entry_id, password, created_at) VALUES (?, ?, ?)",
                (entry_id, password, created_at),
            )
            return PasswordHistoryRecord(cursor.lastrowid, entry_id, password, created_at)

    def list_password_history(self, entry_id: int) -> list[PasswordHistoryRecord]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, entry_id, password, created_at FROM password_history WHERE entry_id = ? "
                "ORDER BY created_at DESC, id DESC",
                (entry_id,),
            )
            return [PasswordHistoryRecord(*row) for row in cursor.fetchall()]

    def replace_all_entries(self, entries: list[VaultEntryRecord]) -> dict[int, int]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM password_history")
            cursor.execute("DELETE FROM vault_entries")
        restored_ids = {}
        for entry in entries:
            restored = self.create_entry(entry)
            if entry.id is not None and restored.id is not None:
                restored_ids[entry.id] = restored.id
        return restored_ids

    def restore_password_history(self, history: list[PasswordHistoryRecord], entry_ids: dict[int, int]) -> None:
        for item in history:
            restored_entry_id = entry_ids.get(item.entry_id)
            if restored_entry_id is None:
                continue
            with self.database_manager.connect() as connection:
                connection.execute(
                    "INSERT INTO password_history (entry_id, password, created_at) VALUES (?, ?, ?)",
                    (restored_entry_id, item.password, item.created_at),
                )

    def find_by_website_and_username(
        self,
        website: str,
        username: str,
    ) -> Optional[VaultEntryRecord]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, title, website, username, password, notes, category, tags, icon, favorite,
                       created_at, updated_at
                FROM vault_entries
                WHERE website = ? AND username = ?
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
                """,
                (website, username),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    def _row_to_entry(self, row) -> VaultEntryRecord:
        return VaultEntryRecord(
            id=row[0],
            title=row[1],
            website=row[2],
            username=row[3],
            password=row[4],
            notes=row[5],
            category=row[6],
            tags=row[7],
            icon=row[8],
            favorite=bool(row[9]),
            created_at=row[10],
            updated_at=row[11],
        )

    def _timestamp(self) -> str:
        return datetime.now(UTC).isoformat()
