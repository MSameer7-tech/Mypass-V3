import sqlite3
from contextlib import contextmanager
import os
from typing import Iterator
from datetime import datetime, UTC
import uuid

from utils.helpers import ensure_directory
from utils.constants import SCHEMA_VERSION


class DatabaseManager:
    def __init__(self, db_file: str):
        ensure_directory(os.path.dirname(db_file))
        self.db_file = db_file
        self.init_db()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_file)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def init_db(self) -> None:
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vault_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    website TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    category TEXT NOT NULL DEFAULT '',
                    tags TEXT NOT NULL DEFAULT '',
                    icon TEXT NOT NULL DEFAULT '',
                    favorite INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS app_metadata (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    version TEXT NOT NULL,
                    created TEXT NOT NULL,
                    vault_id TEXT NOT NULL,
                    argon_parameters TEXT NOT NULL,
                    salt TEXT NOT NULL
                )
                """
            )
            self._ensure_entry_columns(cursor)
            self._migrate_legacy_credentials(cursor)
            self._ensure_metadata(cursor)

    def _ensure_entry_columns(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute("PRAGMA table_info(vault_entries)")
        column_names = {row[1] for row in cursor.fetchall()}
        for name in ("tags", "icon"):
            if name not in column_names:
                cursor.execute(
                    f"ALTER TABLE vault_entries ADD COLUMN {name} TEXT NOT NULL DEFAULT ''"
                )

    def _migrate_legacy_credentials(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='credentials'
            """
        )
        has_legacy_table = cursor.fetchone() is not None
        if not has_legacy_table:
            return

        cursor.execute(
            """
            SELECT website, email, password FROM credentials
            """
        )
        legacy_rows = cursor.fetchall()
        now = self._timestamp()
        for website, email, password in legacy_rows:
            cursor.execute(
                """
                INSERT INTO vault_entries (
                    title, website, username, password, notes, category, tags, icon, favorite,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, '', '', '', '', 0, ?, ?)
                """,
                (website, website, email, password, now, now),
            )

        cursor.execute("DROP TABLE credentials")

    def _ensure_metadata(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute("SELECT COUNT(*) FROM app_metadata")
        if cursor.fetchone()[0] > 0:
            return

        created = self._timestamp()
        cursor.execute(
            """
            INSERT INTO app_metadata (id, version, created, vault_id, argon_parameters, salt)
            VALUES (1, ?, ?, ?, ?, ?)
            """,
            (SCHEMA_VERSION, created, str(uuid.uuid4()), "{}", ""),
        )

    def _timestamp(self) -> str:
        return datetime.now(UTC).isoformat()
