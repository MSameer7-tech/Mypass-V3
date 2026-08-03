import pytest
from services.navigation_service import NavigationService, SelectedEntry

def test_navigation_views():
    nav = NavigationService()
    assert nav.get_current_view() == "login"
    
    view_changes = []
    nav.on_view_changed(lambda v: view_changes.append(v))
    
    nav.navigate_to("dashboard")
    assert nav.get_current_view() == "dashboard"
    assert view_changes == ["dashboard"]
    
    nav.go_back()
    assert nav.get_current_view() == "login"
    assert view_changes == ["dashboard", "login"]

def test_selected_entry_and_history():
    nav = NavigationService()
    
    selections = []
    nav.on_selection_changed(lambda entry: selections.append(entry))
    
    entry1 = SelectedEntry(id=1, title="GitHub", username="user1", url="github.com", category="Work")
    entry2 = SelectedEntry(id=2, title="Amazon", username="user2", url="amazon.com", category="Personal")
    
    nav.set_selected_entry(entry1)
    assert nav.get_selected_entry() == entry1
    assert len(nav.selection_history) == 0
    
    nav.set_selected_entry(entry2)
    assert nav.get_selected_entry() == entry2
    assert nav.selection_history == [entry1]
    
    nav.clear_selection()
    assert nav.get_selected_entry() is None
    assert nav.selection_history == [entry1, entry2]
    assert len(selections) == 3

def test_filters_and_search():
    nav = NavigationService()
    
    filters = []
    searches = []
    nav.on_filter_changed(lambda f: filters.append(f))
    nav.on_search_changed(lambda q: searches.append(q))
    
    nav.set_filter("Favorites")
    assert nav.current_filter == "Favorites"
    assert filters == ["Favorites"]
    
    nav.set_search_query("git")
    assert nav.search_query == "git"
    assert searches == ["git"]

def test_category_counts():
    nav = NavigationService()
    
    counts_updates = []
    nav.on_category_counts_changed(lambda c: counts_updates.append(c))
    
    counts = {"Work": 12, "Personal": 8}
    nav.set_category_counts(counts)
    assert nav.get_category_counts() == counts
    assert counts_updates == [counts]
