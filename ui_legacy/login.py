import customtkinter as ctk

from ui_legacy.components import (
    Card,
    Label,
    PasswordField,
    Button,
    Divider,
    Container
)
from ui_legacy.design_system import typography, spacing

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, *, is_first_launch: bool, on_submit, on_biometric_submit=None, authentication_service=None):
        super().__init__(parent, fg_color="transparent")
        self.is_first_launch = is_first_launch
        self.on_submit = on_submit
        self.on_biometric_submit = on_biometric_submit
        self.authentication_service = authentication_service
        self.error_var = ctk.StringVar(value="")
        self._build_ui()

    def _handle_biometric_unlock(self) -> None:
        if not self.authentication_service or not self.on_biometric_submit:
            return
            
        auth_type = self.authentication_service.get_authentication_type()
        vault_service = self.authentication_service.unlock_vault_with_biometrics(f"Unlock MyPass with {auth_type}")
        if vault_service:
            self.error_var.set("")
            self.password_entry.set_error(None)
            self.on_biometric_submit(vault_service)
        else:
            self.error_var.set("Biometric authentication failed or canceled. Try again or use master password.")
            self.password_entry.set_error("Biometric authentication failed")

    def _build_ui(self) -> None:
        self.card = Card(self, padding=spacing.XL)
        self.card.pack(expand=True, fill="both", padx=spacing.XL, pady=spacing.XL)
        
        container = self.card.get_container()

        title = "Create Master Password" if self.is_first_launch else "Unlock Vault"
        subtitle = (
            "Your master password is never stored. It unlocks the vault from your device."
            if self.is_first_launch
            else "Enter your master password to unlock the vault."
        )

        Label(
            container,
            text=title,
            typography=typography.Display,
            variant="primary",
        ).pack(anchor="w", padx=spacing.XL, pady=(spacing.XXXL, spacing.S))
        
        Label(
            container,
            text=subtitle,
            typography=typography.Body,
            variant="muted",
            wraplength=520,
            justify="left",
        ).pack(anchor="w", padx=spacing.XL, pady=(0, spacing.XL))

        self.password_entry = PasswordField(
            container,
            placeholder="Master Password",
            size="large",
            allow_visibility_toggle=True
        )
        self.password_entry.pack(fill="x", padx=spacing.XL, pady=(0, spacing.L))

        self.confirm_entry = None
        if self.is_first_launch:
            self.confirm_entry = PasswordField(
                container,
                placeholder="Confirm Master Password",
                size="large",
                allow_visibility_toggle=True
            )
            self.confirm_entry.pack(fill="x", padx=spacing.XL, pady=(0, spacing.L))

        self.error_label = Label(
            container,
            text="",
            typography=typography.Body,
            variant="danger",
        )
        # Bind the error_var to a trace to update the label
        self.error_var.trace_add("write", lambda *args: self.error_label.configure(text=self.error_var.get()))
        self.error_label.pack(anchor="w", padx=spacing.XL, pady=(0, spacing.M))

        # Biometric Unlock Button
        if (
            not self.is_first_launch
            and self.authentication_service
            and self.authentication_service.is_biometric_enabled()
            and self.authentication_service.is_biometric_available()
        ):
            auth_type = self.authentication_service.get_authentication_type()
            Button(
                container,
                text=f"Unlock with {auth_type}",
                variant="secondary",
                size="large",
                command=self._handle_biometric_unlock,
            ).pack(fill="x", padx=spacing.XL, pady=(0, spacing.L))

            # Divider
            divider_frame = Container(container)
            divider_frame.pack(fill="x", padx=spacing.XL, pady=(0, spacing.L))
            Divider(divider_frame, padding=0).pack(side="left", expand=True, fill="x")
            Label(divider_frame, text=" OR ", typography=typography.Tiny, variant="muted").pack(side="left", padx=spacing.S)
            Divider(divider_frame, padding=0).pack(side="right", expand=True, fill="x")

        button_text = "Create Vault" if self.is_first_launch else "Unlock"
        Button(
            container,
            text=button_text,
            variant="primary",
            size="large",
            command=self._submit,
        ).pack(fill="x", padx=spacing.XL, pady=(spacing.S, 0))

        self.password_entry.entry.bind("<Return>", lambda event: self._submit())
        if self.confirm_entry is not None:
            self.confirm_entry.entry.bind("<Return>", lambda event: self._submit())

    def _submit(self) -> None:
        password = self.password_entry.get()
        confirm_password = self.confirm_entry.get() if self.confirm_entry is not None else ""

        if not password:
            self.error_var.set("Enter a master password.")
            self.password_entry.set_error("Required")
            return
            
        if self.confirm_entry is not None and password != confirm_password:
            self.error_var.set("Master passwords do not match.")
            self.confirm_entry.set_error("Mismatch")
            return

        try:
            self.on_submit(password)
            if not self.winfo_exists():
                return
            self.error_var.set("")
            self.password_entry.set_error(None)
            if self.confirm_entry:
                self.confirm_entry.set_error(None)
        except Exception as error:
            if self.winfo_exists():
                self.error_var.set(str(error))
                self.password_entry.set_error("Invalid password")

