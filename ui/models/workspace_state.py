from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum, auto

class SortOrder(Enum):
    ALPHABETICAL_ASC = auto()
    ALPHABETICAL_DESC = auto()
    RECENTLY_MODIFIED = auto()
    RECENTLY_USED = auto()
    STRENGTH = auto()

@dataclass(frozen=True)
class FilterState:
    search_query: str = ""
    show_favorites_only: bool = False
    category_filter: Optional[str] = None
    tag_filters: List[str] = field(default_factory=list)
    
@dataclass(frozen=True)
class SortState:
    order: SortOrder = SortOrder.ALPHABETICAL_ASC
    
@dataclass(frozen=True)
class WorkspaceState:
    filter_state: FilterState = field(default_factory=FilterState)
    sort_state: SortState = field(default_factory=SortState)
