from PySide6.QtCore import QObject, Signal

class ViewModel(QObject):
    """
    Base class for all ViewModels in the PySide6 MyPass application.
    Enforces a consistent contract for state updates.
    """
    
    # Emitted when the ViewModel begins or ends a background operation
    busyChanged = Signal(bool)
    
    # Emitted when a transient error occurs that should be shown to the user (e.g., via a Toast)
    errorOccurred = Signal(str)
    
    # Emitted when general state changes that views need to reflect
    stateChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
