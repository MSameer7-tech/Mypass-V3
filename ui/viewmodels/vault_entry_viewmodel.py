from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from database.models import VaultEntryRecord

def _format_time_ago(iso_string: str) -> str:
    """Formats an ISO string into '4 weeks ago', 'Yesterday', etc."""
    if not iso_string:
        return "Unknown"
    
    try:
        # Assuming UTC timezone for simplicity. Real app uses proper timezone parsing
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        days = diff.days
        if days == 0:
            return "Today"
        elif days == 1:
            return "Yesterday"
        elif days < 7:
            return f"{days} days ago"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days < 365:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
    except ValueError:
        return iso_string

@dataclass(frozen=True)
class VaultEntryViewModel:
    """
    Immutable ViewModel bridging VaultEntryRecord and Presentation Layer.
    Keeps raw data for sorting, provides formatted strings for display.
    """
    id: Optional[int]
    
    # Raw values (for sorting & domain logic)
    raw_title: str
    raw_username: str
    raw_website: str
    raw_created_at: str
    raw_updated_at: str
    raw_favorite: bool
    raw_category: str
    raw_tags: str
    
    # Display Properties (for UI presentation)
    display_title: str
    display_username: str
    display_url: str
    icon_path: str
    formatted_created_at: str
    formatted_updated_at: str
    
    # We deliberately don't expose password or notes in the List ViewModel
    # to keep memory footprint low and avoid accidental leaks in list views.
    # Those are fetched/decrypted only when viewing details.
    
    @classmethod
    def from_record(cls, record: VaultEntryRecord) -> 'VaultEntryViewModel':
        # Default icon handling (in Phase 5 we'll resolve actual SVGs)
        icon = record.icon if record.icon else "default_key.svg"
        
        return cls(
            id=record.id,
            raw_title=record.title,
            raw_username=record.username,
            raw_website=record.website,
            raw_created_at=record.created_at,
            raw_updated_at=record.updated_at,
            raw_favorite=record.favorite,
            raw_category=record.category,
            raw_tags=record.tags,
            
            display_title=record.title or "Untitled Entry",
            display_username=record.username or "No username",
            display_url=record.website or "",
            icon_path=icon,
            formatted_created_at=_format_time_ago(record.created_at),
            formatted_updated_at=_format_time_ago(record.updated_at)
        )
