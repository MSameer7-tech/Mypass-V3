from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import weakref

@dataclass
class SelectedEntry:
    id: int
    title: str
    username: str
    url: str
    category: str
    favorite: bool = False
    data: Optional[Any] = None

class NavigationService:
    """
    Manages application routing, active views, dialog states, and selection context.
    Decouples navigation logic from UI components.
    """
    def __init__(self):
        self._current_view: str = "login"
        self._current_selected_entry: Optional[SelectedEntry] = None
        self._current_filter: str = "all"
        self._search_query: str = ""
        self._category_counts: Dict[str, int] = {}
        
        # Observers for state changes
        self._view_listeners: List[Callable] = []
        self._selection_listeners: List[Callable] = []
        self._filter_listeners: List[Callable] = []
        self._search_listeners: List[Callable] = []
        self._counts_listeners: List[Callable] = []
        
        # Breadcrumbs & selection history
        self._history: List[str] = ["login"]
        self._selection_history: List[SelectedEntry] = []
        
        # Liveness Adapters
        self._liveness_adapters: List[Callable[[Any], Optional[bool]]] = []

    def register_liveness_adapter(self, adapter: Callable[[Any], Optional[bool]]) -> None:
        if adapter not in self._liveness_adapters:
            self._liveness_adapters.append(adapter)

    def _is_alive(self, listener: Callable) -> bool:
        target = getattr(listener, '__self__', None)
        if target is None:
            return True
            
        for adapter in self._liveness_adapters:
            result = adapter(target)
            if result is not None:
                return result
                
        if hasattr(target, 'winfo_exists'):
            try:
                return bool(target.winfo_exists())
            except Exception:
                return False
                
        return True

    def _add_listener(self, listeners: List[Callable], listener: Callable) -> None:
        if listener not in listeners:
            listeners.append(listener)

    def _notify(self, listeners: List[Callable], *args: Any) -> None:
        alive_listeners = []
        for listener in list(listeners):
            if self._is_alive(listener):
                alive_listeners.append(listener)
                try:
                    listener(*args)
                except Exception:
                    pass
        listeners[:] = alive_listeners
        
    def navigate_to(self, view_name: str, clear_history: bool = False) -> None:
        """Navigate to a top-level view."""
        if clear_history:
            self._history.clear()
            
        self._history.append(view_name)
        self._current_view = view_name
        self._notify_view_changed()
        
    def go_back(self) -> bool:
        """Navigate back to the previous view."""
        if len(self._history) > 1:
            self._history.pop() # Remove current
            self._current_view = self._history[-1]
            self._notify_view_changed()
            return True
        return False
        
    def get_current_view(self) -> str:
        return self._current_view
        
    def set_selected_entry(self, entry: Optional[SelectedEntry]) -> None:
        """Set the currently focused password entry."""
        if self._current_selected_entry != entry:
            if self._current_selected_entry is not None:
                self._selection_history.append(self._current_selected_entry)
            self._current_selected_entry = entry
            self._notify_selection_changed()
            
    def get_selected_entry(self) -> Optional[SelectedEntry]:
        return self._current_selected_entry

    def clear_selection(self) -> None:
        self.set_selected_entry(None)

    @property
    def selection_history(self) -> List[SelectedEntry]:
        return self._selection_history.copy()

    # Filter & Search
    @property
    def current_filter(self) -> str:
        return self._current_filter

    def set_filter(self, filter_name: str) -> None:
        if self._current_filter != filter_name:
            self._current_filter = filter_name
            self._notify_filter_changed()

    @property
    def search_query(self) -> str:
        return self._search_query

    def set_search_query(self, query: str) -> None:
        if self._search_query != query:
            self._search_query = query
            self._notify_search_changed()

    # Category Counts
    def set_category_counts(self, counts: Dict[str, int]) -> None:
        self._category_counts = counts.copy()
        self._notify_counts_changed()

    def get_category_counts(self) -> Dict[str, int]:
        return self._category_counts.copy()
        
    # Observer Registration
    def on_view_changed(self, listener: Callable[[str], None]) -> None:
        self._add_listener(self._view_listeners, listener)
        
    def on_selection_changed(self, listener: Callable[[Optional[SelectedEntry]], None]) -> None:
        self._add_listener(self._selection_listeners, listener)

    def on_filter_changed(self, listener: Callable[[str], None]) -> None:
        self._add_listener(self._filter_listeners, listener)

    def on_search_changed(self, listener: Callable[[str], None]) -> None:
        self._add_listener(self._search_listeners, listener)

    def on_category_counts_changed(self, listener: Callable[[Dict[str, int]], None]) -> None:
        self._add_listener(self._counts_listeners, listener)
        
    def _notify_view_changed(self) -> None:
        self._notify(self._view_listeners, self._current_view)
                
    def _notify_selection_changed(self) -> None:
        self._notify(self._selection_listeners, self._current_selected_entry)

    def _notify_filter_changed(self) -> None:
        self._notify(self._filter_listeners, self._current_filter)

    def _notify_search_changed(self) -> None:
        self._notify(self._search_listeners, self._search_query)

    def _notify_counts_changed(self) -> None:
        self._notify(self._counts_listeners, self._category_counts)
