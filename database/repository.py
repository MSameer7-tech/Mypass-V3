from typing import Optional

from database.database import DatabaseManager
from database.models import AppMetadataRecord, VaultEntryRecord
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
                SELECT version, created, vault_id, argon_parameters, salt
                FROM app_metadata
                WHERE id = 1
                """
            )
            row = cursor.fetchone()
            return AppMetadataRecord(*row)

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

    def get_entry_by_id(self, entry_id: int) -> Optional[VaultEntryRecord]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, title, website, username, password, notes, category, favorite,
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
                SELECT id, title, website, username, password, notes, category, favorite,
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
                SELECT id, title, website, username, password, notes, category, favorite,
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
                SELECT id, title, website, username, password, notes, category, favorite,
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
                    title, website, username, password, notes, category, favorite,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.title,
                    entry.website,
                    entry.username,
                    entry.password,
                    entry.notes,
                    entry.category,
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
                    category = ?, favorite = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    entry.title,
                    entry.website,
                    entry.username,
                    entry.password,
                    entry.notes,
                    entry.category,
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

    def find_by_website_and_username(
        self,
        website: str,
        username: str,
    ) -> Optional[VaultEntryRecord]:
        with self.database_manager.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, title, website, username, password, notes, category, favorite,
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
            favorite=bool(row[7]),
            created_at=row[8],
            updated_at=row[9],
        )

    def _timestamp(self) -> str:
        return datetime.now(UTC).isoformat()
