from PySide6.QtCore import QObject
from services.password_generator import PasswordGenerator, PasswordGeneratorOptions
from ui.dialogs.password_generator_dialog import PasswordGeneratorDialog
from ui.actions.action_manager import ActionManager
from ui.actions.vault import VaultActions
from ui.actions.commands import CopyFieldCommand

class PasswordGeneratorCoordinator(QObject):
    """
    Orchestrates the password generation workflow.
    Keeps business logic out of the UI dialog.
    """
    def __init__(self, generator_service: PasswordGenerator, clipboard_service, notification_service, session_controller, parent=None):
        super().__init__(parent)
        self.generator_service = generator_service
        self.clipboard_service = clipboard_service
        self.notification_service = notification_service
        self.session_controller = session_controller
        
        self.dialog = None
        self.current_options = PasswordGeneratorOptions()
        
        ActionManager.instance().action_triggered.connect(self._on_action_triggered)
        self.session_controller.state_changed.connect(self._on_session_state_changed)
        
    def _on_session_state_changed(self, state, context):
        from ui.session.context import SessionState
        if state in (SessionState.LOCKED, SessionState.NO_VAULT):
            if self.dialog:
                self.dialog.reject()
                self.dialog.deleteLater()
                self.dialog = None
            self.current_options = PasswordGeneratorOptions() # Reset to default
            
    def _on_action_triggered(self, action, payload):
        if action == VaultActions.GENERATE_PASSWORD:
            self.show_dialog()
            
    def show_dialog(self):
        if not self.dialog:
            self.dialog = PasswordGeneratorDialog()
            self.dialog.options_changed.connect(self._on_options_changed)
            self.dialog.generate_requested.connect(self.generate)
            self.dialog.copy_requested.connect(self._on_copy_requested)
            
        self.generate()
        self.dialog.exec()
        
    def _on_options_changed(self, options: PasswordGeneratorOptions):
        self.current_options = options
        self.generate()
        
    def generate(self):
        try:
            password = self.generator_service.generate(self.current_options)
            strength = self.generator_service.evaluate_strength(password)
            if self.dialog:
                self.dialog.set_password(password, strength)
        except ValueError as e:
            if self.notification_service:
                self.notification_service.show_error("Generation Error", str(e))
                
    def _on_copy_requested(self, password: str):
        if not password:
            return
            
        # We push this directly since it's not part of the vault undo stack,
        # but we can just execute the command directly for non-undoable actions if we don't have a global stack.
        # Actually, CopyFieldCommand just executes.
        cmd = CopyFieldCommand("Generated Password", password, self.clipboard_service, self.notification_service)
        cmd.execute()
        
        if self.dialog:
            self.dialog.accept()
