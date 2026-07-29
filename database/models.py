from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VaultEntryRecord:
    id: Optional[int]
    title: str
    website: str
    username: str
    password: str
    notes: str
    category: str
    favorite: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class AppMetadataRecord:
    version: str
    created: str
    vault_id: str
    argon_parameters: str
    salt: str
