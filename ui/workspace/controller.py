from PySide6.QtCore import QObject, Signal

class WorkspaceController(QObject):
    """
    Coordinates interactions between Sidebar, ContentRegion, and DetailsPane.
    Prevents widgets from talking directly to each other.
    """
    
    # Signals to instruct views to change
    content_page_changed = Signal(int)
    details_page_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def handle_sidebar_selection(self, item_id: str):
        """Called when a sidebar item is clicked."""
        print(f"Sidebar selected: {item_id}")
        
        # In a real implementation, we would map item_id to specific pages.
        # For now, we just ensure we stay on the Welcome Page (0) or Nothing Selected (0).
        self.content_page_changed.emit(0)
        self.details_page_changed.emit(0)
