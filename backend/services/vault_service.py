from typing import Optional

from database.models import AppMetadataRecord, PasswordHistoryRecord, VaultEntryRecord
from database.repository import VaultRepository


class EncryptionAdapter:
    def encrypt(self, value: str) -> str:
        raise NotImplementedError

    def decrypt(self, value: str) -> str:
        raise NotImplementedError


class VaultService:
    def __init__(
        self,
        repository: VaultRepository,
        encryption_service: EncryptionAdapter,
    ):
        self.repository = repository
        self.encryption_service = encryption_service

    def get_total_credentials(self) -> int:
        return self.repository.count_entries()

    def get_metadata(self) -> AppMetadataRecord:
        return self.repository.get_metadata()

    def save_credential(self, website: str, email: str, password: str) -> str:
        existing_entry = self.repository.find_by_website_and_username(website, email)
        saved_entry = self.save_entry(
            title=website,
            website=website,
            username=email,
            password=password,
            notes="",
            category="",
            favorite=False,
            entry_id=existing_entry.id if existing_entry else None,
        )
        return "updated" if existing_entry else "created"

    def save_entry(
        self,
        title: str,
        website: str,
        username: str,
        password: str,
        notes: str = "",
        category: str = "",
        tags: str = "",
        icon: str = "",
        favorite: bool = False,
        entry_id: Optional[int] = None,
    ) -> VaultEntryRecord:
        encrypted_password = self.encryption_service.encrypt(password)
        encrypted_notes = self.encryption_service.encrypt(notes) if notes else ""
        existing_entry = self.repository.get_entry_by_id(entry_id) if entry_id is not None else None
        if (
            existing_entry is not None
            and self.encryption_service.decrypt(existing_entry.password) != password
        ):
            self.repository.add_password_history(existing_entry.id, existing_entry.password)
        base_entry = VaultEntryRecord(
            id=entry_id,
            title=title,
            website=website,
            username=username,
            password=encrypted_password,
            notes=encrypted_notes,
            category=category,
            tags=tags,
            icon=icon,
            favorite=favorite,
            created_at=existing_entry.created_at if existing_entry else "",
            updated_at=existing_entry.updated_at if existing_entry else "",
        )

        if existing_entry is None:
            stored_entry = self.repository.create_entry(base_entry)
        else:
            stored_entry = self.repository.update_entry(base_entry)
        return self._decrypt_entry(stored_entry)

    def find_credential(self, website: str) -> Optional[VaultEntryRecord]:
        stored_record = self.repository.get_latest_entry_by_website(website)
        if stored_record is None:
            return None
        return self._decrypt_entry(stored_record)

    def list_entries_by_website(self, website: str) -> list[VaultEntryRecord]:
        return [self._decrypt_entry(entry) for entry in self.repository.list_entries_by_website(website)]

    def list_all_entries(self) -> list[VaultEntryRecord]:
        return [self._decrypt_entry(entry) for entry in self.repository.list_all_entries()]

    def search_entries(self, query: str) -> list[VaultEntryRecord]:
        normalized_query = self._normalize_search_value(query)
        if not normalized_query:
            return self.list_all_entries()
        matches = []
        for entry in self.list_all_entries():
            searchable_values = (entry.title, entry.website, entry.username, entry.category, entry.tags)
            if any(normalized_query in self._normalize_search_value(value) for value in searchable_values):
                matches.append(entry)
        return matches

    def delete_entry(self, entry_id: int) -> None:
        self.repository.delete_entry_by_id(entry_id)

    def get_entry(self, entry_id: int) -> Optional[VaultEntryRecord]:
        stored_record = self.repository.get_entry_by_id(entry_id)
        if stored_record is None:
            return None
        return self._decrypt_entry(stored_record)

    def get_password_history(self, entry_id: int) -> list[PasswordHistoryRecord]:
        return [
            PasswordHistoryRecord(
                id=item.id,
                entry_id=item.entry_id,
                password=self.encryption_service.decrypt(item.password),
                created_at=item.created_at,
            )
            for item in self.repository.list_password_history(entry_id)
        ]

    def restore_password_from_history(self, entry_id: int, history_id: int) -> VaultEntryRecord:
        history = next(
            (item for item in self.get_password_history(entry_id) if item.id == history_id),
            None,
        )
        if history is None:
            raise ValueError("Password history entry was not found.")
        entry = self._decrypt_entry(self.repository.get_entry_by_id(entry_id))
        return self.save_entry(
            title=entry.title,
            website=entry.website,
            username=entry.username,
            password=history.password,
            notes=entry.notes,
            category=entry.category,
            tags=entry.tags,
            icon=entry.icon,
            favorite=entry.favorite,
            entry_id=entry_id,
        )

    def replace_vault_contents(
        self,
        entries: list[VaultEntryRecord],
        history: list[PasswordHistoryRecord],
    ) -> None:
        encrypted_entries = [
            VaultEntryRecord(
                id=entry.id,
                title=entry.title,
                website=entry.website,
                username=entry.username,
                password=self.encryption_service.encrypt(entry.password),
                notes=self.encryption_service.encrypt(entry.notes) if entry.notes else "",
                category=entry.category,
                tags=entry.tags,
                icon=entry.icon,
                favorite=entry.favorite,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
            )
            for entry in entries
        ]
        entry_ids = self.repository.replace_all_entries(encrypted_entries)
        encrypted_history = [
            PasswordHistoryRecord(
                id=None,
                entry_id=item.entry_id,
                password=self.encryption_service.encrypt(item.password),
                created_at=item.created_at,
            )
            for item in history
        ]
        self.repository.restore_password_history(encrypted_history, entry_ids)

    @staticmethod
    def _normalize_search_value(value: str) -> str:
        normalized = value.strip().lower()
        for prefix in ("https://", "http://"):
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :]
        normalized = normalized.removeprefix("www.").rstrip("/")
        return "".join(character for character in normalized if character.isalnum())

    def _decrypt_entry(self, stored_record: VaultEntryRecord) -> VaultEntryRecord:
        decrypted_password = self.encryption_service.decrypt(stored_record.password)
        decrypted_notes = (
            self.encryption_service.decrypt(stored_record.notes) if stored_record.notes else ""
        )
        return VaultEntryRecord(
            id=stored_record.id,
            title=stored_record.title,
            website=stored_record.website,
            username=stored_record.username,
            password=decrypted_password,
            notes=decrypted_notes,
            category=stored_record.category,
            tags=stored_record.tags,
            icon=stored_record.icon,
            favorite=stored_record.favorite,
            created_at=stored_record.created_at,
            updated_at=stored_record.updated_at,
        )
