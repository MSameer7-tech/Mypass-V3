import platform
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from config import BG_COLOR
from services.master_password_service import InvalidMasterPasswordError, MasterPasswordService
from services.password_generator import PasswordGenerator, PasswordGeneratorOptions
from services.validation import CredentialInput, validate_credential_input
from services.vault_service import VaultService
from services.breach_detection import BreachStatus

import webbrowser
from ui_legacy.components import (
    Button, Label, Card, TextField, PasswordField, SearchField,
    TextArea, Badge, Divider, PasswordStrengthIndicator, Dropdown,
    EmptyState, ToastManager, Checkbox, Container, Radio
)
from ui_legacy.dialogs import PasswordGeneratorDialog, SettingsDialog, AddEditCredentialDialog
from ui_legacy.shell import ApplicationShell
from services.navigation_service import SelectedEntry
from ui_legacy.login import LoginView
from utils.constants import APP_NAME, APP_VERSION, WINDOW_HEIGHT, WINDOW_WIDTH
from utils.helpers import resource_path
from ui_legacy.design_system import typography, spacing, themes


class DashboardWindow(ctk.CTk):
    def __init__(
        self,
        master_password_service: MasterPasswordService,
        password_generator: PasswordGenerator,
        password_health_service,
        backup_service,
        import_service,
        clipboard_service,
        session_lock_service,
        breach_detection_service=None,
        authentication_service=None,
    ):
        super().__init__(fg_color=themes.DarkTheme.background)
        self.master_password_service = master_password_service
        self.vault_service: VaultService | None = None
        self.password_generator = password_generator
        self.password_health_service = password_health_service
        self.backup_service = backup_service
        self.import_service = import_service
        self.clipboard_service = clipboard_service
        self.session_lock_service = session_lock_service
        self.breach_detection_service = breach_detection_service
        self.authentication_service = authentication_service
        
        self.card = None
        self.footer = None
        self.empty_state_label = None
        self.auto_lock_job = None
        self.current_entry_id = None
        self._breach_job = None
        self._last_checked_password = None
        
        self.shell: ApplicationShell | None = None
        self.current_filter: str = "all"
        self.search_query: str = ""

        self._configure_window()
        self.logo_image = self._load_logo()
        self.toast_manager = ToastManager(self)
        
        self.bind_all("<KeyPress>", self._record_activity, add="+")
        self.bind_all("<ButtonPress>", self._record_activity, add="+")
        self._show_login_view()

    def _configure_window(self) -> None:
        self.title(APP_NAME)
        self.geometry("1120x700")
        self.minsize(900, 560)
        self._set_window_icon()

    def _set_window_icon(self) -> None:
        try:
            if platform.system() == "Windows":
                self.iconbitmap(resource_path("assets/icon.ico"))
                return
            icon_image = Image.open(resource_path("assets/logo.png"))
            self.window_icon = ImageTk.PhotoImage(icon_image)
            self.wm_iconphoto(True, self.window_icon)
        except Exception:
            return

    def _load_logo(self):
        for asset_name in ("app_icon.png", "logo.png"):
            try:
                return ctk.CTkImage(
                    Image.open(resource_path(f"assets/{asset_name}")),
                    size=(48, 48),
                )
            except Exception:
                continue
        return None

    def _clear_main_content(self) -> None:
        for child in self.winfo_children():
            if hasattr(self, "toast_manager") and child is getattr(self.toast_manager, "toast_frame", None):
                continue
            child.destroy()

    def _show_login_view(self) -> None:
        if self.auto_lock_job is not None:
            self.after_cancel(self.auto_lock_job)
            self.auto_lock_job = None
        self._clear_main_content()
        self.vault_service = None
        login_view = LoginView(
            self,
            is_first_launch=not self.master_password_service.is_configured(),
            on_submit=self._handle_master_password_submit,
            on_biometric_submit=self._handle_biometric_submit,
            authentication_service=self.authentication_service,
        )
        login_view.pack(expand=True, fill="both")

    def _handle_master_password_submit(self, master_password: str) -> VaultService:
        try:
            if self.master_password_service.is_configured():
                self.vault_service = self.master_password_service.unlock_vault(master_password)
            else:
                self.vault_service = self.master_password_service.create_vault_service(master_password)
        except InvalidMasterPasswordError as error:
            raise error

        if self.authentication_service and self.authentication_service.is_secure_storage_available():
            self.authentication_service.store_secret(self.vault_service.encryption_service.key)

        self._build_ui()
        self.session_lock_service.unlock()
        self._monitor_auto_lock()
        return self.vault_service

    def _handle_biometric_submit(self, vault_service) -> None:
        self.vault_service = vault_service
        self._build_ui()
        self.session_lock_service.unlock()
        self._monitor_auto_lock()

    def _build_ui(self) -> None:
        self._clear_main_content()
        self.shell = ApplicationShell(
            self,
            on_add_item=self.open_add_credential_dialog,
            on_lock=self.lock_vault,
            on_settings=self.open_settings_dialog,
            on_open_url=self.open_url_in_browser,
            on_edit_item=self.edit_credential_by_id,
            on_delete_item=self.delete_credential_by_id,
            on_copy_password=self.copy_password_str,
            on_copy_username=self.copy_username_str,
            on_copy_totp=self.copy_totp_str,
            on_history_item=self.show_password_history,
        )
        self.shell.pack(expand=True, fill="both")

        self.shell.sidebar.on_filter_selected = self._handle_filter_selected
        self.shell.toolbar.on_search_change = self._handle_search_change
        self.shell.workspace.password_list.on_item_selected = self._handle_item_selected
        self.shell.workspace.password_list.on_add_clicked = self.open_add_credential_dialog

        self._bind_shortcuts()
        self.refresh_workspace()

    def refresh_workspace(self) -> None:
        if self.vault_service is None or self.shell is None:
            return
        all_entries = self.vault_service.list_all_entries()

        counts = {"all": len(all_entries), "favorites": 0}
        for item in all_entries:
            if getattr(item, "favorite", False):
                counts["favorites"] += 1
            cat = getattr(item, "category", None) or "Personal"
            counts[cat] = counts.get(cat, 0) + 1
        self.shell.sidebar.update_counters(counts)

        filtered = []
        for item in all_entries:
            if self.current_filter == "favorites":
                if not getattr(item, "favorite", False):
                    continue
            elif self.current_filter != "all":
                if (getattr(item, "category", None) or "Personal") != self.current_filter:
                    continue
            if self.search_query:
                q = self.search_query.lower()
                title_match = q in (item.title or "").lower()
                user_match = q in (item.username or "").lower()
                web_match = q in (item.website or "").lower()
                if not (title_match or user_match or web_match):
                    continue
            filtered.append(item)

        selected_entries = [
            SelectedEntry(
                id=item.id,
                title=item.title or "Untitled",
                username=item.username or "",
                url=item.website or "",
                category=item.category or "Personal",
                favorite=bool(getattr(item, "favorite", False)),
                data=item
            )
            for item in filtered
        ]
        self.shell.workspace.set_items(selected_entries, select_first=True)
        if selected_entries:
            self._handle_item_selected(selected_entries[0])
        else:
            self.current_entry_id = None

    def refresh_credential_count(self) -> None:
        self.refresh_workspace()

    def open_add_credential_dialog(self) -> None:
        AddEditCredentialDialog(
            self,
            self.vault_service,
            password_generator=self.password_generator,
            on_saved=self.refresh_workspace
        )

    def open_edit_credential_dialog(self, entry_id: int) -> None:
        AddEditCredentialDialog(
            self,
            self.vault_service,
            password_generator=self.password_generator,
            entry_id=entry_id,
            on_saved=self.refresh_workspace
        )

    def edit_credential_by_id(self, entry_id: int) -> None:
        self.open_edit_credential_dialog(entry_id)

    def delete_credential_by_id(self, entry_id: int) -> None:
        if self.vault_service is None:
            return
        if messagebox.askyesno("Delete Credential", "Are you sure you want to delete this credential?", parent=self):
            try:
                self.vault_service.delete_entry(entry_id)
                self.toast_manager.show("Credential deleted")
                self.refresh_workspace()
            except Exception as e:
                self.toast_manager.show(f"Could not delete: {str(e)}", is_error=True)

    def open_settings_dialog(self) -> None:
        SettingsDialog(
            self,
            self.master_password_service,
            self.authentication_service,
            self.toast_manager,
            lambda: self.lock_vault("Vault locked due to master password change"),
            on_backup=self.create_backup,
            on_restore=self.restore_backup,
            on_import=self.import_passwords,
        )

    def open_url_in_browser(self, url: str) -> None:
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        try:
            webbrowser.open(url)
        except Exception:
            self.toast_manager.show("Could not open URL", is_error=True)

    def copy_password_str(self, password: str) -> None:
        if not password:
            return
        self.clipboard_service.copy(password, scheduler=self)
        self.toast_manager.show("Password copied. Clears in 20 seconds.")

    def copy_username_str(self, username: str) -> None:
        if not username:
            return
        self.clipboard_service.copy(username, scheduler=self)
        self.toast_manager.show("Username copied to clipboard")

    def copy_totp_str(self, totp: str) -> None:
        if not totp:
            return
        self.clipboard_service.copy(totp, scheduler=self)
        self.toast_manager.show("TOTP copied to clipboard")

    def _handle_filter_selected(self, filter_id: str) -> None:
        self.current_filter = filter_id
        self.refresh_workspace()

    def _handle_search_change(self, query: str) -> None:
        self.search_query = query
        self.refresh_workspace()

    def _handle_item_selected(self, entry: SelectedEntry) -> None:
        if self.shell is None:
            return
        self.current_entry_id = entry.id
        self.shell.workspace.details_pane.display_entry(entry)
        self._check_breach_for_entry(entry)

    def _check_breach_for_entry(self, entry: SelectedEntry) -> None:
        if self.breach_detection_service is None:
            return
        pwd = ""
        if entry.data and hasattr(entry.data, "password"):
            pwd = str(entry.data.password or "")
        if not pwd:
            return
            
        def _do_check():
            try:
                res = self.breach_detection_service.check_password(pwd)
                is_breached = (res.status == BreachStatus.BREACHED)
                def _cb():
                    if self.winfo_exists() and self.current_entry_id == entry.id:
                        if self.shell and self.shell.workspace:
                            badge = self.shell.workspace.details_pane.security_badge
                            if is_breached:
                                badge.set_text("Breached")
                                badge.set_variant("danger")
                self.after(0, _cb)
            except Exception:
                pass
        threading.Thread(target=_do_check, daemon=True).start()

    def _bind_shortcuts(self) -> None:
        self.bind("<Command-s>", lambda event: self.save_password())
        self.bind("<Command-f>", lambda event: self.find_password())
        self.bind("<Command-g>", lambda event: self.generate_password())
        self.bind("<Control-s>", lambda event: self.save_password())
        self.bind("<Control-f>", lambda event: self.find_password())
        self.bind("<Control-g>", lambda event: self.generate_password())

    def _set_auto_lock_timeout(self, selection: str) -> None:
        minutes = int(selection.split()[0])
        self.session_lock_service.set_timeout(minutes * 60)
        self.toast_manager.show(f"Auto-lock set to {minutes} minutes")

    def _record_activity(self, _event=None) -> None:
        if self.vault_service is not None:
            if self.session_lock_service.should_lock():
                self.lock_vault(message="Vault locked due to inactivity")
                return
            self.session_lock_service.record_activity()

    def _monitor_auto_lock(self) -> None:
        if self.vault_service is None:
            return
        if self.session_lock_service.should_lock():
            self.lock_vault(message="Vault locked due to inactivity")
            return
        self.auto_lock_job = self.after(1000, self._monitor_auto_lock)

    def lock_vault(self, message: str = "Vault locked") -> None:
        self.session_lock_service.lock()
        self.clipboard_service.clear_now()
        self._show_login_view()
        self.toast_manager.show(message)

    def save_password(self) -> None:
        self.open_add_credential_dialog()

    def find_password(self) -> None:
        if self.shell and self.shell.toolbar:
            self.shell.toolbar.focus_search()

    def generate_password(self) -> None:
        try:
            generated_password = self.password_generator.generate(PasswordGeneratorOptions())
            self.copy_password_str(generated_password)
        except ValueError as error:
            self.toast_manager.show(str(error), is_error=True)

    def show_password_history(self, entry_id: int = None) -> None:
        target_id = entry_id or self.current_entry_id
        if self.vault_service is None or target_id is None:
            self.toast_manager.show("Select an entry to view its history", is_error=True)
            return
        history = self.vault_service.get_password_history(target_id)
        if not history:
            self.toast_manager.show("No previous passwords for this entry", is_error=True)
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Password History")
        dialog.geometry("480x360")
        dialog.configure(fg_color=themes.DarkTheme.surface)
        dialog.transient(self)

        selected_history_id = ctk.StringVar(value=str(history[0].id))
        Label(dialog, text="Password History", typography=typography.Title).pack(anchor="w", padx=spacing.L, pady=(spacing.L, spacing.M))

        for item in history:
            Radio(
                dialog,
                text=f"{item.created_at[:10]}    {'*' * min(len(item.password), 16)}",
                variable=selected_history_id,
                value=str(item.id)
            ).pack(anchor="w", padx=spacing.L, pady=spacing.XS)

        def restore_selected() -> None:
            if not messagebox.askyesno("Restore password", "Restore this password?", parent=dialog):
                return
            self.vault_service.restore_password_from_history(
                target_id, int(selected_history_id.get())
            )
            dialog.destroy()
            self.refresh_workspace()
            self.toast_manager.show("Previous password restored")

        Button(dialog, text="Restore Selected", command=restore_selected).pack(fill="x", padx=spacing.L, pady=spacing.L)

    def create_backup(self) -> None:
        if self.vault_service is None:
            return
        backup_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".backup",
            filetypes=[("MyPass encrypted backup", "*.backup")],
        )
        if not backup_path:
            return
        try:
            self.backup_service.create_backup(self.vault_service, backup_path)
        except Exception as error:
            self.toast_manager.show(str(error), is_error=True)
            return
        self.toast_manager.show("Encrypted backup created")

    def restore_backup(self) -> None:
        if self.vault_service is None:
            return
        backup_path = filedialog.askopenfilename(
            parent=self, filetypes=[("MyPass encrypted backup", "*.backup")]
        )
        if not backup_path:
            return
        if not messagebox.askyesno(
            "Restore backup", "Replace the current vault with this backup?", parent=self
        ):
            return
        try:
            self.backup_service.restore_backup(self.vault_service, backup_path)
        except Exception as error:
            self.toast_manager.show("Could not restore this backup", is_error=True)
            return
        self.current_entry_id = None
        self.refresh_credential_count()
        self.toast_manager.show("Backup restored")

    def import_passwords(self) -> None:
        if self.vault_service is None:
            return
        source_prompt = ctk.CTkInputDialog(
            text="Source: Chrome, Edge, Firefox, Bitwarden, KeePass, or CSV", title="Import Passwords"
        )
        source = source_prompt.get_input()
        if not source:
            return
        source_lookup = {item.lower(): item for item in self.import_service.SUPPORTED_SOURCES}
        source = source_lookup.get(source.strip().lower(), source.strip())
        csv_path = filedialog.askopenfilename(parent=self, filetypes=[("CSV files", "*.csv")])
        if not csv_path:
            return
        try:
            count = self.import_service.import_csv(self.vault_service, csv_path, source)
        except Exception as error:
            self.toast_manager.show(str(error), is_error=True)
            return
        self.refresh_credential_count()
        self.toast_manager.show(f"Imported {count} encrypted entries")
