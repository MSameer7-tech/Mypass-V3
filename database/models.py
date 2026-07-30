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
    tags: str
    icon: str
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
    biometric_enabled: bool = False
    biometric_platform: str | None = None
    biometric_enrolled_at: float | None = None
    biometric_prompt_state: str = "never"
    last_master_password_change: str | None = None


@dataclass(frozen=True)
class PasswordHistoryRecord:
    id: Optional[int]
    entry_id: int
    password: str
    created_at: str
