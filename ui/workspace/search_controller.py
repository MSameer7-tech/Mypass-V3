from PySide6.QtCore import QObject, Signal, QTimer
from typing import List, Tuple
import re

class SearchController(QObject):
    """
    Manages search state, debouncing, query normalization, history, and highlighting bounds.
    Emits signals when the canonical search query changes so the FilterModel can update.
    """
    search_changed = Signal(str)
    
    def __init__(self, debounce_ms: int = 200, parent=None):
        super().__init__(parent)
        self.debounce_ms = debounce_ms
        self._current_query = ""
        self._normalized_query = ""
        self._history: List[str] = []
        
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(self.debounce_ms)
        self._timer.timeout.connect(self._apply_search)
        
    def set_query(self, query: str):
        """Called by the Toolbar search input on every keystroke."""
        self._current_query = query
        self._timer.start()
        
    def clear(self):
        """Instantly clears the search without debouncing."""
        self._timer.stop()
        self._current_query = ""
        self._apply_search()
        
    def get_query(self) -> str:
        return self._normalized_query
        
    def get_history(self) -> List[str]:
        return list(self._history)
        
    def _apply_search(self):
        normalized = self._current_query.strip().lower()
        if normalized == self._normalized_query:
            return
            
        self._normalized_query = normalized
        if normalized and normalized not in self._history:
            self._history.append(normalized)
            if len(self._history) > 10:
                self._history.pop(0)
                
        self.search_changed.emit(self._normalized_query)
        
    def compute_highlights(self, text: str) -> List[Tuple[int, int]]:
        """
        Computes character ranges (start, length) that match the current query.
        Returns empty list if no query or no match.
        """
        if not self._normalized_query or not text:
            return []
            
        # Case insensitive find
        lower_text = text.lower()
        ranges = []
        start = 0
        q_len = len(self._normalized_query)
        
        while True:
            idx = lower_text.find(self._normalized_query, start)
            if idx == -1:
                break
            ranges.append((idx, q_len))
            start = idx + q_len
            
        return ranges
