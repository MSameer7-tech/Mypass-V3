from dataclasses import dataclass
from typing import Optional

from database.models import VaultEntryRecord

@dataclass(frozen=True)
class EntryDetailsViewModel:
    """
    Immutable ViewModel containing sensitive fields for the Details Pane.
    Should be purged from memory when the entry is deselected or session locks.
    """
    id: int
    title: str
    username: str
    website: str
    password: str
    notes: str
    
    # We could add TOTP placeholder here or fetch it separately
    
    @classmethod
    def from_record(cls, record: VaultEntryRecord) -> 'EntryDetailsViewModel':
        return cls(
            id=record.id,
            title=record.title or "",
            username=record.username or "",
            website=record.website or "",
            password=record.password or "",
            notes=record.notes or ""
        )
