import customtkinter as ctk

from services.password_generator import PasswordGeneratorOptions, PasswordGenerator
from services.validation import validate_credential_input, CredentialInput
from ui_legacy.components import (
    BaseDialog, Button, Label, Checkbox, 
    TextField, PasswordField, Divider, Container,
    TextArea, Dropdown
)
from ui_legacy.design_system import typography, spacing

def flash_entry_error(entry, error_color=None, default_color=None) -> None:
    # We now use the state API on input fields
    if hasattr(entry, "set_error"):
        entry.set_error("Invalid input")
        # clear error after short delay
        entry.after(1000, lambda: entry.set_error(None))


class PasswordGeneratorDialog(BaseDialog):
    def __init__(self, parent, on_generate):
        super().__init__(parent, title="Password Generator", width=400, height=480)
        self.on_generate = on_generate

        self.length_var = ctk.StringVar(value="16")
        self.uppercase_var = ctk.BooleanVar(value=True)
        self.lowercase_var = ctk.BooleanVar(value=True)
        self.numbers_var = ctk.BooleanVar(value=True)
        self.symbols_var = ctk.BooleanVar(value=True)
        self.similar_var = ctk.BooleanVar(value=False)
        self.ambiguous_var = ctk.BooleanVar(value=False)
        self.error_var = ctk.StringVar(value="")
        self._build_ui()

    def _build_ui(self) -> None:
        # Length row
        length_row = Container(self.body_frame)
        length_row.pack(fill="x", pady=(0, spacing.M))
        
        Label(length_row, text="Length").pack(side="left")
        
        self.length_entry = TextField(length_row, size="small", textvariable=self.length_var)
        self.length_entry.pack(side="right")
        self.length_entry.entry.configure(width=80)

        # Checkboxes
        for label, variable in (
            ("Uppercase", self.uppercase_var),
            ("Lowercase", self.lowercase_var),
            ("Numbers", self.numbers_var),
            ("Symbols", self.symbols_var),
            ("Exclude similar characters", self.similar_var),
            ("Avoid ambiguous characters", self.ambiguous_var),
        ):
            Checkbox(self.body_frame, text=label, variable=variable).pack(anchor="w", pady=spacing.XS)

        self.error_label = Label(self.body_frame, text="", variant="danger", typography=typography.Caption)
        self.error_var.trace_add("write", lambda *args: self.error_label.configure(text=self.error_var.get()))
        self.error_label.pack(anchor="w", pady=(spacing.S, 0))

        self.add_standard_buttons(
            primary_text="Generate Password",
            primary_command=self._submit,
            secondary_command=self.destroy
        )

    def _submit(self) -> None:
        try:
            options = PasswordGeneratorOptions(
                length=int(self.length_var.get()),
                uppercase=self.uppercase_var.get(),
                lowercase=self.lowercase_var.get(),
                numbers=self.numbers_var.get(),
                symbols=self.symbols_var.get(),
                exclude_similar=self.similar_var.get(),
                avoid_ambiguous=self.ambiguous_var.get(),
            )
            self.on_generate(options)
        except ValueError as error:
            self.error_var.set(str(error))
            return
        self.destroy()


class SettingsDialog(BaseDialog):
    def __init__(
        self,
        parent,
        master_password_service,
        authentication_service,
        toast_manager,
        on_password_changed,
        on_backup=None,
        on_restore=None,
        on_import=None,
    ):
        super().__init__(parent, title="Settings", width=420, height=580)
        self.master_password_service = master_password_service
        self.authentication_service = authentication_service
        self.toast_manager = toast_manager
        self.on_password_changed = on_password_changed
        self.on_backup = on_backup
        self.on_restore = on_restore
        self.on_import = on_import

        self.biometric_var = ctk.BooleanVar(
            value=self.authentication_service.is_biometric_enabled()
            if self.authentication_service
            else False
        )
        self.lock_on_sleep_var = ctk.BooleanVar(value=True)
        self.lock_on_idle_var = ctk.BooleanVar(value=True)
        self.clear_clipboard_var = ctk.BooleanVar(value=True)
        self.require_master_password_var = ctk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self) -> None:
        Label(self.body_frame, text="Security", typography=typography.Title, variant="muted").pack(anchor="w", pady=(0, spacing.S))

        if not self.authentication_service or not self.authentication_service.is_secure_storage_available():
            Label(self.body_frame, text="Biometric Unlock: Unavailable", variant="danger").pack(anchor="w", pady=spacing.XS)
        elif not self.authentication_service.is_biometric_available():
            Label(self.body_frame, text="Biometric Unlock: Hardware Not Found", variant="danger").pack(anchor="w", pady=spacing.XS)
        else:
            auth_type = self.authentication_service.get_authentication_type()
            Checkbox(
                self.body_frame,
                text=f"Enable {auth_type}",
                variable=self.biometric_var,
                command=self._toggle_biometrics,
            ).pack(anchor="w", pady=spacing.XS)

        for label, variable in (
            ("Lock on sleep", self.lock_on_sleep_var),
            ("Lock on idle", self.lock_on_idle_var),
            ("Clear clipboard", self.clear_clipboard_var),
            ("Require master password after restart", self.require_master_password_var),
        ):
            Checkbox(self.body_frame, text=label, variable=variable).pack(anchor="w", pady=spacing.XS)
            
        if self.authentication_service and self.authentication_service.is_biometric_enabled():
            Button(
                self.body_frame,
                text="Disable Biometrics",
                variant="danger",
                size="small",
                command=self._disable_biometrics_btn,
            ).pack(anchor="w", pady=(spacing.M, 0))
            
        Divider(self.body_frame).pack(fill="x", pady=spacing.L)

        Label(self.body_frame, text="Account", typography=typography.Title, variant="muted").pack(anchor="w", pady=(0, spacing.S))
        
        Button(
            self.body_frame,
            text="Change Master Password",
            variant="secondary",
            command=self._open_change_password_dialog,
        ).pack(fill="x", pady=(spacing.S, 0))

        if self.on_backup or self.on_restore or self.on_import:
            Divider(self.body_frame).pack(fill="x", pady=spacing.L)
            Label(self.body_frame, text="Vault Data", typography=typography.Title, variant="muted").pack(anchor="w", pady=(0, spacing.S))
            btn_frame = Container(self.body_frame)
            btn_frame.pack(fill="x", pady=(spacing.S, 0))
            if self.on_backup:
                Button(btn_frame, text="Backup", variant="secondary", command=self.on_backup).pack(side="left", expand=True, fill="x", padx=(0, spacing.XS))
            if self.on_restore:
                Button(btn_frame, text="Restore", variant="secondary", command=self.on_restore).pack(side="left", expand=True, fill="x", padx=spacing.XS)
            if self.on_import:
                Button(btn_frame, text="Import", variant="secondary", command=self.on_import).pack(side="left", expand=True, fill="x", padx=(spacing.XS, 0))

    def _toggle_biometrics(self) -> None:
        if self.biometric_var.get():
            auth_type = self.authentication_service.get_authentication_type()
            success = self.authentication_service.enable_biometrics(f"Enroll {auth_type} for MyPass")
            if success:
                if hasattr(self.parent, "vault_service") and self.parent.vault_service:
                    self.authentication_service.store_secret(self.parent.vault_service.encryption_service.key)
                self.toast_manager.show(f"{auth_type} enabled successfully.")
            else:
                self.biometric_var.set(False)
                self.toast_manager.show(f"{auth_type} enrollment canceled.", is_error=True)
        else:
            self.authentication_service.disable_biometrics()
            self.toast_manager.show("Biometric unlock disabled.")

    def _disable_biometrics_btn(self) -> None:
        if self.authentication_service and self.authentication_service.is_secure_storage_available():
            try:
                self.authentication_service.delete_secret()
            except Exception:
                pass
        if self.authentication_service:
            self.authentication_service.disable_biometrics()
        self.biometric_var.set(False)
        self.toast_manager.show("Biometrics fully disabled and secrets cleared.")
        self.destroy()

    def _open_change_password_dialog(self):
        ChangePasswordDialog(
            self, 
            self.master_password_service, 
            self.authentication_service, 
            self.toast_manager,
            self.on_password_changed
        )


class ChangePasswordDialog(BaseDialog):
    def __init__(self, parent, master_password_service, authentication_service, toast_manager, on_success):
        super().__init__(parent, title="Change Master Password", width=400, height=440)
        self.settings_dialog = parent
        self.master_password_service = master_password_service
        self.authentication_service = authentication_service
        self.toast_manager = toast_manager
        self.on_success = on_success

        self.current_password_var = ctk.StringVar()
        self.new_password_var = ctk.StringVar()
        self.confirm_password_var = ctk.StringVar()
        self.error_var = ctk.StringVar(value="")
        
        self._build_ui()

    def _build_ui(self) -> None:
        self.current_pw = PasswordField(self.body_frame, label="Current Password", textvariable=self.current_password_var)
        self.current_pw.pack(fill="x", pady=(0, spacing.M))
        
        self.new_pw = PasswordField(self.body_frame, label="New Password", textvariable=self.new_password_var)
        self.new_pw.pack(fill="x", pady=(0, spacing.M))
        
        self.confirm_pw = PasswordField(self.body_frame, label="Confirm New Password", textvariable=self.confirm_password_var)
        self.confirm_pw.pack(fill="x", pady=(0, spacing.S))
        
        self.error_label = Label(self.body_frame, text="", variant="danger", typography=typography.Caption)
        self.error_var.trace_add("write", lambda *args: self.error_label.configure(text=self.error_var.get()))
        self.error_label.pack(anchor="w", pady=(spacing.S, 0))

        self.add_standard_buttons(
            primary_text="Change Password",
            primary_command=self._submit,
            secondary_command=self.destroy
        )
        
    def _submit(self):
        current_pw = self.current_password_var.get()
        new_pw = self.new_password_var.get()
        confirm_pw = self.confirm_password_var.get()
        
        self.current_pw.set_error(None)
        self.new_pw.set_error(None)
        self.confirm_pw.set_error(None)
        
        if not current_pw or not new_pw or not confirm_pw:
            self.error_var.set("All fields are required.")
            if not current_pw: self.current_pw.set_error("Required")
            if not new_pw: self.new_pw.set_error("Required")
            if not confirm_pw: self.confirm_pw.set_error("Required")
            return
            
        if new_pw != confirm_pw:
            self.error_var.set("New passwords do not match.")
            self.confirm_pw.set_error("Mismatch")
            return
            
        if current_pw == new_pw:
            self.error_var.set("New password must be different.")
            self.new_pw.set_error("Must be different")
            return
            
        try:
            self.master_password_service.change_master_password(current_pw, new_pw)
        except Exception as e:
            self.error_var.set(str(e))
            self.current_pw.set_error("Invalid")
            return
            
        if self.authentication_service and self.authentication_service.is_secure_storage_available():
            try:
                self.authentication_service.delete_secret()
            except Exception:
                pass
            self.authentication_service.disable_biometrics()
            
            from tkinter import messagebox
            auth_type = self.authentication_service.get_authentication_type()
            msg = (
                "Your master password has been changed.\n\n"
                f"For security, biometric unlock ({auth_type}) has been disabled because the vault key changed.\n\n"
                "Would you like to enable it again?"
            )
            if messagebox.askyesno("Password Changed", msg, parent=self):
                if self.authentication_service.enable_biometrics(f"Enroll {auth_type} for MyPass"):
                    self.toast_manager.show(f"{auth_type} enabled successfully.")
                else:
                    self.toast_manager.show(f"{auth_type} enrollment canceled.", is_error=True)
            else:
                self.toast_manager.show("Password changed successfully.")
        else:
            self.toast_manager.show("Password changed successfully.")

        self.destroy()
        if hasattr(self, "settings_dialog"):
            self.settings_dialog.destroy()
        self.on_success()


class AddEditCredentialDialog(BaseDialog):
    """
    Modal dialog for adding a new credential or editing an existing one.
    """
    def __init__(
        self,
        parent,
        vault_service,
        password_generator: Optional[PasswordGenerator] = None,
        entry_id: Optional[int] = None,
        on_saved: Optional[Callable[[], None]] = None
    ):
        title = "Edit Credential" if entry_id else "Add New Credential"
        super().__init__(parent, title=title, width=460, height=680)
        self.vault_service = vault_service
        self.password_generator = password_generator or PasswordGenerator()
        self.entry_id = entry_id
        self.on_saved = on_saved
        
        self.title_var = ctk.StringVar()
        self.website_var = ctk.StringVar()
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.category_var = ctk.StringVar(value="Personal")
        self.favorite_var = ctk.BooleanVar(value=False)
        
        self.notes_val = ""
        
        self._load_existing_if_needed()
        self._build_ui()

    def _load_existing_if_needed(self) -> None:
        if self.entry_id and self.vault_service:
            items = self.vault_service.list_all_entries()
            for item in items:
                if item.id == self.entry_id:
                    self.title_var.set(item.title or "")
                    self.website_var.set(item.website or "")
                    self.username_var.set(item.username or "")
                    self.password_var.set(item.password or "")
                    self.category_var.set(item.category or "Personal")
                    self.favorite_var.set(bool(item.favorite))
                    self.notes_val = item.notes or ""
                    break

    def _build_ui(self) -> None:
        self.title_field = TextField(
            self.body_frame,
            label="Title *",
            placeholder="e.g. GitHub, Google",
            textvariable=self.title_var
        )
        self.title_field.pack(fill="x", pady=(0, spacing.M))
        
        self.website_field = TextField(
            self.body_frame,
            label="Website URL",
            placeholder="e.g. https://github.com",
            textvariable=self.website_var
        )
        self.website_field.pack(fill="x", pady=(0, spacing.M))
        
        self.username_field = TextField(
            self.body_frame,
            label="Username / Email *",
            placeholder="e.g. user@example.com",
            textvariable=self.username_var
        )
        self.username_field.pack(fill="x", pady=(0, spacing.M))
        
        # Password + Generate button row
        pwd_label = Label(self.body_frame, text="Password *", typography=typography.Caption)
        pwd_label.pack(anchor="w", pady=(0, 2))
        
        pwd_row = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        pwd_row.pack(fill="x", pady=(0, spacing.M))
        pwd_row.grid_columnconfigure(0, weight=1)
        
        self.password_field = PasswordField(
            pwd_row,
            label="",
            textvariable=self.password_var,
            allow_copy=True
        )
        self.password_field.grid(row=0, column=0, sticky="ew")
        
        gen_btn = Button(
            pwd_row,
            text="Generate",
            variant="secondary",
            size="small",
            command=self._generate_password
        )
        gen_btn.grid(row=0, column=1, padx=(spacing.S, 0))
        
        # Category Dropdown
        cat_lbl = Label(self.body_frame, text="Category", typography=typography.Caption)
        cat_lbl.pack(anchor="w", pady=(0, 2))
        self.category_dropdown = Dropdown(
            self.body_frame,
            values=["Personal", "Work", "Banking", "Social", "Development", "Shopping", "Gaming"],
            variable=self.category_var
        )
        self.category_dropdown.pack(fill="x", pady=(0, spacing.M))
        
        # Secure Notes
        self.notes_field = TextArea(
            self.body_frame,
            label="Secure Notes",
            height=72
        )
        self.notes_field.pack(fill="x", pady=(0, spacing.M))
        if self.notes_val:
            self.notes_field.textbox.insert("1.0", self.notes_val)
            
        Checkbox(
            self.body_frame,
            text="Mark as Favorite ★",
            variable=self.favorite_var
        ).pack(anchor="w", pady=(0, spacing.M))
        
        self.error_label = Label(self.body_frame, text="", variant="danger", typography=typography.Caption)
        self.error_label.pack(anchor="w", pady=(0, spacing.S))
        
        self.add_standard_buttons(
            primary_text="Save Credential",
            primary_command=self._submit,
            secondary_command=self.destroy
        )

    def _generate_password(self) -> None:
        try:
            pwd = self.password_generator.generate(PasswordGeneratorOptions())
            self.password_var.set(pwd)
        except Exception:
            pass

    def _submit(self) -> None:
        title = self.title_var.get().strip()
        website = self.website_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get()
        notes = self.notes_field.get().strip()
        category = self.category_var.get()
        favorite = self.favorite_var.get()
        
        validation = validate_credential_input(
            CredentialInput(
                title=title,
                website=website,
                username=username,
                password=password
            )
        )
        
        self.title_field.set_error(None)
        self.username_field.set_error(None)
        self.password_field.set_error(None)
        
        if not validation["title"]:
            self.title_field.set_error("Title required")
        if not validation["username"]:
            self.username_field.set_error("Username required")
        if not validation["password"]:
            self.password_field.set_error("Password required")
            
        if not all(validation.values()):
            self.error_label.configure(text="Please fill out all required fields (*).")
            return
            
        try:
            self.vault_service.save_entry(
                title=title,
                website=website,
                username=username,
                password=password,
                notes=notes,
                category=category,
                favorite=favorite,
                entry_id=self.entry_id
            )
            self.destroy()
            if self.on_saved:
                self.on_saved()
        except Exception as e:
            self.error_label.configure(text=f"Error saving: {str(e)}")

