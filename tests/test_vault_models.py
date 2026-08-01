import pytest
from PySide6.QtCore import Qt

from ui.models.roles import VaultRoles
from ui.viewmodels.vault_entry_viewmodel import VaultEntryViewModel
from ui.models.model_context import ModelContext, LoadingState
from database.models import VaultEntryRecord

def create_mock_record(id, title):
    return VaultEntryRecord(
        id=id,
        title=title,
        website="",
        username="",
        password="",
        notes="",
        category="",
        tags="",
        icon="",
        favorite=False,
        created_at="2026-07-30T10:00:00Z",
        updated_at="2026-07-30T10:00:00Z"
    )

def test_vault_list_model_insertion_and_count():
    context = ModelContext()
    model = context.vault_list_model
    
    assert model.rowCount() == 0
    
    records = [create_mock_record(i, f"Title {i}") for i in range(100)]
    viewmodels = [VaultEntryViewModel.from_record(r) for r in records]
    
    model.replace_entries(viewmodels)
    
    assert model.rowCount() == 100
    
    # Insert one
    new_vm = VaultEntryViewModel.from_record(create_mock_record(100, "New Title"))
    model.insert_entry(new_vm)
    
    assert model.rowCount() == 101

def test_vault_list_model_update_emits_signal():
    context = ModelContext()
    model = context.vault_list_model
    
    records = [create_mock_record(1, "Title 1")]
    viewmodels = [VaultEntryViewModel.from_record(r) for r in records]
    model.replace_entries(viewmodels)
    
    signal_emitted = False
    def on_data_changed(top_left, bottom_right, roles):
        nonlocal signal_emitted
        signal_emitted = True
        assert top_left.row() == 0
        assert bottom_right.row() == 0
        
    model.dataChanged.connect(on_data_changed)
    
    updated_vm = VaultEntryViewModel.from_record(create_mock_record(1, "Updated Title"))
    model.update_entry(updated_vm)
    
    assert signal_emitted
    
    # Check data was updated
    idx = model.index(0, 0)
    assert model.data(idx, VaultRoles.TitleRole) == "Updated Title"

def test_vault_list_model_removal():
    context = ModelContext()
    model = context.vault_list_model
    
    records = [create_mock_record(1, "Title 1"), create_mock_record(2, "Title 2")]
    viewmodels = [VaultEntryViewModel.from_record(r) for r in records]
    model.replace_entries(viewmodels)
    
    assert model.rowCount() == 2
    model.remove_entry(1)
    
    assert model.rowCount() == 1
    idx = model.index(0, 0)
    assert model.data(idx, VaultRoles.TitleRole) == "Title 2"

def test_vault_filter_model_text_search():
    context = ModelContext()
    list_model = context.vault_list_model
    filter_model = context.vault_filter_model
    
    records = [
        create_mock_record(1, "Apple"),
        create_mock_record(2, "Banana"),
        create_mock_record(3, "Cherry")
    ]
    viewmodels = [VaultEntryViewModel.from_record(r) for r in records]
    list_model.replace_entries(viewmodels)
    
    assert filter_model.rowCount() == 3
    
    filter_model.set_search_query("ba")
    assert filter_model.rowCount() == 1
    idx = filter_model.index(0, 0)
    assert filter_model.data(idx, VaultRoles.TitleRole) == "Banana"

def test_model_context_clear_on_lock():
    context = ModelContext()
    list_model = context.vault_list_model
    selection = context.selection_manager
    
    # Populate
    records = [create_mock_record(1, "Apple")]
    viewmodels = [VaultEntryViewModel.from_record(r) for r in records]
    list_model.replace_entries(viewmodels)
    
    context.set_state(LoadingState.READY)
    
    # Simulate Coordinator Clear
    list_model.replace_entries([])
    selection.clear_selection()
    context.set_state(LoadingState.EMPTY)
    
    assert list_model.rowCount() == 0
    assert not selection.has_selection
    assert context.state == LoadingState.EMPTY

def test_selection_manager_force_emit():
    context = ModelContext()
    list_model = context.vault_list_model
    selection = context.selection_manager
    
    records = [create_mock_record(1, "Apple")]
    viewmodels = [VaultEntryViewModel.from_record(r) for r in records]
    list_model.replace_entries(viewmodels)
    
    emitted_vms = []
    selection.selection_changed.connect(lambda vm: emitted_vms.append(vm))
    
    # First select
    selection.select_entry_by_id(1, force_emit=True)
    assert len(emitted_vms) == 1
    assert emitted_vms[0].display_title == "Apple"
    
    # Second select with force_emit=True even though it is already selected
    selection.select_entry_by_id(1, force_emit=True)
    assert len(emitted_vms) == 2

