from typing import Optional

from database.models import AppMetadataRecord, VaultEntryRecord
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
        favorite: bool = False,
        entry_id: Optional[int] = None,
    ) -> VaultEntryRecord:
        encrypted_password = self.encryption_service.encrypt(password)
        existing_entry = self.repository.get_entry_by_id(entry_id) if entry_id is not None else None
        base_entry = VaultEntryRecord(
            id=entry_id,
            title=title,
            website=website,
            username=username,
            password=encrypted_password,
            notes=notes,
            category=category,
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

    def _decrypt_entry(self, stored_record: VaultEntryRecord) -> VaultEntryRecord:
        decrypted_password = self.encryption_service.decrypt(stored_record.password)
        return VaultEntryRecord(
            id=stored_record.id,
            title=stored_record.title,
            website=stored_record.website,
            username=stored_record.username,
            password=decrypted_password,
            notes=stored_record.notes,
            category=stored_record.category,
            favorite=stored_record.favorite,
            created_at=stored_record.created_at,
            updated_at=stored_record.updated_at,
        )
