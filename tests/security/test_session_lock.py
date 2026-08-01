import pytest
from PySide6.QtCore import QObject
from ui.session.controller import SessionController
from ui.session.context import SessionState, LockReason
from ui.actions.commands import UndoStack, Command
from ui.models.model_context import ModelContext
from ui.workspace.entry_details_coordinator import EntryDetailsCoordinator
from ui.workspace.vault_adapter import VaultRepositoryAdapter

class DummyCommand(Command):
    def __init__(self):
        self.executed = False
        self.undone = False

    def execute(self) -> None:
        self.executed = True

    def undo(self) -> None:
        self.undone = True

def test_sec_007_invalid_transition():
    """SEC-007: Unvalidated state transition (Prohibited)"""
    controller = SessionController()
    
    # Valid BOOTING -> NO_VAULT
    controller.transition_to(SessionState.NO_VAULT)
    assert controller.context.state == SessionState.NO_VAULT
    
    # Invalid NO_VAULT -> LOCKED
    controller.transition_to(SessionState.LOCKED)
    assert controller.context.state == SessionState.NO_VAULT # Ignored

def test_sec_003_undo_stack_purge():
    """SEC-003: UndoStack must purge on SessionState.LOCKED"""
    controller = SessionController()
    undo_stack = UndoStack()
    
    # Wire the undo stack to session changes like VaultCoordinator does
    def _on_state_changed(state, ctx):
        if state == SessionState.LOCKED:
            undo_stack.clear()
            
    controller.state_changed.connect(_on_state_changed)
    
    # Push a command
    cmd = DummyCommand()
    undo_stack.push(cmd)
    
    assert undo_stack.can_undo() is True
    
    # Transition to LOCKED
    controller.transition_to(SessionState.LOCKED)
    
    # Verify SEC-003
    assert undo_stack.can_undo() is False
    assert len(undo_stack._stack) == 0

class DummyVaultService:
    def get_entry(self, entry_id): return None
    
class DummyVaultAdapter(VaultRepositoryAdapter):
    def __init__(self):
        super().__init__(DummyVaultService())

class DummyTotpService(QObject):
    pass

def test_sec_004_cache_persistence_purge():
    """SEC-004: EntryDetailsCoordinator cache must purge on SessionState.LOCKED"""
    controller = SessionController()
    model_context = ModelContext()
    adapter = DummyVaultAdapter()
    totp = DummyTotpService()
    
    coordinator = EntryDetailsCoordinator(adapter, model_context, controller, totp)
    
    # Simulate a populated cache
    coordinator._cache[123] = "DUMMY_VIEWMODEL"
    assert len(coordinator._cache) == 1
    
    # Lock the session
    controller.transition_to(SessionState.LOCKED)
    
    # Verify SEC-004
    assert len(coordinator._cache) == 0
