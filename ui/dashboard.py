import platform

import customtkinter as ctk
from PIL import Image, ImageTk

from config import (
    ACCENT_COLOR,
    APP_FONT,
    BG_COLOR,
    BORDER_COLOR,
    CARD_COLOR,
    ERROR_COLOR,
    FOCUS_BORDER,
    HOVER_ACCENT_COLOR,
    INPUT_COLOR,
    MUTED_TEXT,
    SUCCESS_COLOR,
    WARNING_COLOR,
)
from services.master_password_service import InvalidMasterPasswordError, MasterPasswordService
from services.password_generator import PasswordGenerator, PasswordGeneratorOptions
from services.validation import CredentialInput, validate_credential_input
from services.vault_service import VaultService
from ui.dialogs import PasswordGeneratorDialog, ToastManager, flash_entry_error
from ui.login import LoginView
from utils.constants import APP_NAME, APP_VERSION, WINDOW_HEIGHT, WINDOW_WIDTH
from utils.helpers import resource_path


class DashboardWindow(ctk.CTk):
    def __init__(
        self,
        master_password_service: MasterPasswordService,
        password_generator: PasswordGenerator,
        password_health_service,
        clipboard_service,
        session_lock_service,
    ):
        super().__init__(fg_color=BG_COLOR)
        self.master_password_service = master_password_service
        self.vault_service: VaultService | None = None
        self.password_generator = password_generator
        self.password_health_service = password_health_service
        self.clipboard_service = clipboard_service
        self.session_lock_service = session_lock_service
        self.show_password_value = False
        self.card = None
        self.footer = None
        self.empty_state_label = None
        self.auto_lock_job = None

        self._configure_window()
        self.password_var = ctk.StringVar()
        self.password_var.trace_add("write", self.update_strength_bar)

        self.icons = self._load_icons()
        self.logo_image = self._load_logo()
        self.toast_manager = ToastManager(self, APP_FONT)
        self.bind_all("<KeyPress>", self._record_activity, add="+")
        self.bind_all("<ButtonPress>", self._record_activity, add="+")
        self._show_login_view()

    def _configure_window(self) -> None:
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
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

    def _load_icons(self) -> dict[str, ctk.CTkImage | None]:
        icon_names = ("eye", "eye-off", "copy", "search")
        icons = {}
        for icon_name in icon_names:
            try:
                icons[icon_name] = ctk.CTkImage(
                    Image.open(resource_path(f"assets/{icon_name}.png")),
                    size=(18, 18),
                )
            except Exception:
                icons[icon_name] = None
        return icons

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
            if child is not self.toast_manager.toast_frame:
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
        )
        login_view.pack(expand=True, fill="both")

    def _build_ui(self) -> None:
        self._clear_main_content()
        self.card = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.card.pack(expand=True, fill="both", padx=24, pady=24)

        self._build_header()
        self._build_form()
        self._build_footer()
        self._bind_shortcuts()
        self.refresh_credential_count()

    def _handle_master_password_submit(self, master_password: str) -> None:
        try:
            if self.master_password_service.is_configured():
                self.vault_service = self.master_password_service.unlock_vault(master_password)
            else:
                self.vault_service = self.master_password_service.create_vault_service(master_password)
        except InvalidMasterPasswordError as error:
            raise error

        self._build_ui()
        self.session_lock_service.unlock()
        self._monitor_auto_lock()

    def _build_header(self) -> None:
        header_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        header_frame.pack(pady=(30, 20))

        if self.logo_image:
            logo_label = ctk.CTkLabel(header_frame, image=self.logo_image, text="")
            logo_label.pack(side="left", padx=(0, 15))

        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=(APP_FONT, 22, "bold"),
            text_color="white",
        ).pack(anchor="w")

        controls = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls.pack(side="right", padx=(60, 0))
        auto_lock_var = ctk.StringVar(value="5 min")
        ctk.CTkOptionMenu(
            controls,
            values=["1 min", "5 min", "10 min", "15 min", "30 min"],
            variable=auto_lock_var,
            width=100,
            height=30,
            fg_color=INPUT_COLOR,
            button_color=BORDER_COLOR,
            button_hover_color=FOCUS_BORDER,
            command=self._set_auto_lock_timeout,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            controls,
            text="Lock Now",
            width=82,
            height=30,
            fg_color=INPUT_COLOR,
            hover_color=BORDER_COLOR,
            border_width=1,
            border_color=BORDER_COLOR,
            command=self.lock_vault,
        ).pack(side="left")
        ctk.CTkLabel(
            title_frame,
            text="Secure Password Vault",
            font=(APP_FONT, 12),
            text_color=MUTED_TEXT,
        ).pack(anchor="w")

    def _build_form(self) -> None:
        self.title_entry = self._build_labeled_entry(
            "Title",
            "Amazon Shopping",
            pady=(10, 2),
        )
        self.website_entry = self._build_labeled_entry(
            "Website",
            "amazon.com",
            pady=(15, 2),
            with_search=True,
        )
        self.email_entry = self._build_labeled_entry(
            "Email or Username",
            "john@example.com",
            pady=(15, 2),
        )
        self.password_entry = self._build_password_section()
        self._build_strength_section()
        self._build_entry_metadata()
        self._build_button_row()
        ctk.CTkLabel(
            self.card,
            text="Passwords are securely stored locally.",
            font=(APP_FONT, 11),
            text_color=MUTED_TEXT,
        ).pack(side="bottom", pady=(0, 25))

    def _build_entry_metadata(self) -> None:
        self.category_var = ctk.StringVar(value="Personal")
        ctk.CTkLabel(
            self.card, text="Category", font=(APP_FONT, 12), text_color=MUTED_TEXT
        ).pack(anchor="w", padx=40, pady=(14, 2))
        ctk.CTkOptionMenu(
            self.card,
            values=["Personal", "Social", "Banking", "Development", "Work", "Gaming", "Shopping"],
            variable=self.category_var,
            height=38,
            fg_color=INPUT_COLOR,
            button_color=BORDER_COLOR,
            button_hover_color=FOCUS_BORDER,
        ).pack(fill="x", padx=40)
        self.tags_entry = self._build_labeled_entry("Tags", "shopping, retail", pady=(12, 2))
        self.icon_entry = self._build_labeled_entry("Icon", "globe", pady=(12, 2))
        ctk.CTkLabel(
            self.card, text="Secure Notes", font=(APP_FONT, 12), text_color=MUTED_TEXT
        ).pack(anchor="w", padx=40, pady=(12, 2))
        self.notes_entry = ctk.CTkTextbox(
            self.card,
            height=72,
            fg_color=INPUT_COLOR,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=8,
        )
        self.notes_entry.pack(fill="x", padx=40)
        self.favorite_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.card,
            text="Favorite",
            variable=self.favorite_var,
            font=(APP_FONT, 12),
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_ACCENT_COLOR,
        ).pack(anchor="w", padx=40, pady=(10, 0))

    def _build_labeled_entry(
        self,
        label: str,
        placeholder: str,
        pady: tuple[int, int],
        with_search: bool = False,
    ):
        ctk.CTkLabel(
            self.card,
            text=label,
            font=(APP_FONT, 12),
            text_color=MUTED_TEXT,
        ).pack(anchor="w", padx=40, pady=pady)

        if with_search:
            entry_frame = ctk.CTkFrame(self.card, fg_color="transparent")
            entry_frame.pack(fill="x", padx=40)
            entry = self._create_entry(entry_frame, placeholder)
            entry.pack(side="left", expand=True, fill="x")
            ctk.CTkButton(
                entry_frame,
                text="",
                image=self.icons.get("search"),
                width=40,
                height=40,
                fg_color=INPUT_COLOR,
                hover_color=BORDER_COLOR,
                border_width=1,
                border_color=BORDER_COLOR,
                corner_radius=8,
                cursor="hand2",
                command=self.find_password,
            ).pack(side="right", padx=(8, 0))
            return entry

        entry = self._create_entry(self.card, placeholder)
        entry.pack(fill="x", padx=40)
        return entry

    def _create_entry(self, parent, placeholder: str, show: str | None = None, textvariable=None):
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=40,
            fg_color=INPUT_COLOR,
            border_color=BORDER_COLOR,
            corner_radius=8,
            border_width=1,
            show=show,
            textvariable=textvariable,
        )
        entry.bind("<FocusIn>", lambda event: entry.configure(border_color=FOCUS_BORDER))
        entry.bind("<FocusOut>", lambda event: entry.configure(border_color=BORDER_COLOR))
        return entry

    def _build_password_section(self):
        ctk.CTkLabel(
            self.card,
            text="Password",
            font=(APP_FONT, 12),
            text_color=MUTED_TEXT,
        ).pack(anchor="w", padx=40, pady=(15, 2))

        password_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        password_frame.pack(fill="x", padx=40)

        entry = self._create_entry(
            password_frame,
            "Generate or enter password",
            show="*",
            textvariable=self.password_var,
        )
        entry.pack(side="left", expand=True, fill="x")

        self.eye_button = ctk.CTkButton(
            password_frame,
            text="",
            image=self.icons.get("eye"),
            width=40,
            height=40,
            fg_color=INPUT_COLOR,
            hover_color=BORDER_COLOR,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=8,
            cursor="hand2",
            command=self.toggle_password_visibility,
        )
        self.eye_button.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            password_frame,
            text="",
            image=self.icons.get("copy"),
            width=40,
            height=40,
            fg_color=INPUT_COLOR,
            hover_color=BORDER_COLOR,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=8,
            cursor="hand2",
            command=self.copy_password,
        ).pack(side="left", padx=(8, 0))
        return entry

    def _build_strength_section(self) -> None:
        strength_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        strength_frame.pack(fill="x", padx=40, pady=(10, 0))

        self.strength_bar = ctk.CTkProgressBar(
            strength_frame,
            height=4,
            progress_color=BORDER_COLOR,
            fg_color=BORDER_COLOR,
            corner_radius=2,
        )
        self.strength_bar.pack(fill="x")
        self.strength_bar.set(0)

        self.strength_label = ctk.CTkLabel(
            strength_frame,
            text="",
            font=(APP_FONT, 11),
            text_color=MUTED_TEXT,
            height=14,
        )
        self.strength_label.pack(anchor="w", pady=(4, 0))

    def _build_button_row(self) -> None:
        button_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        button_frame.pack(fill="x", padx=40, pady=(20, 20))

        ctk.CTkButton(
            button_frame,
            text="Generate",
            height=40,
            fg_color=INPUT_COLOR,
            hover_color=BORDER_COLOR,
            text_color="white",
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=8,
            cursor="hand2",
            font=(APP_FONT, 13, "bold"),
            command=self.generate_password,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            button_frame,
            text="Options",
            height=40,
            width=78,
            fg_color=INPUT_COLOR,
            hover_color=BORDER_COLOR,
            text_color="white",
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=8,
            cursor="hand2",
            command=self.open_generator_options,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            button_frame,
            text="Save",
            height=40,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_ACCENT_COLOR,
            text_color="white",
            corner_radius=8,
            cursor="hand2",
            font=(APP_FONT, 13, "bold"),
            command=self.save_password,
        ).pack(side="right", expand=True, fill="x", padx=(6, 0))

    def _build_footer(self) -> None:
        self.footer = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.footer.pack(fill="x", side="bottom", padx=20, pady=10)

        ctk.CTkLabel(
            self.footer,
            text=f"{APP_NAME} v{APP_VERSION}",
            font=(APP_FONT, 11),
            text_color=MUTED_TEXT,
        ).pack(side="left")

        self.empty_state_label = ctk.CTkLabel(
            self.footer,
            text="",
            font=(APP_FONT, 12),
            text_color=MUTED_TEXT,
        )
        self.empty_state_label.pack(side="right")

    def _bind_shortcuts(self) -> None:
        self.bind("<Command-s>", lambda event: self.save_password())
        self.bind("<Command-f>", lambda event: self.find_password())
        self.bind("<Command-g>", lambda event: self.generate_password())
        self.bind("<Return>", lambda event: self.save_password())
        self.bind("<Control-s>", lambda event: self.save_password())
        self.bind("<Control-f>", lambda event: self.find_password())
        self.bind("<Control-g>", lambda event: self.generate_password())

    def refresh_credential_count(self) -> None:
        if self.vault_service is None or self.empty_state_label is None:
            return
        count = self.vault_service.get_total_credentials()
        if count == 0:
            self.empty_state_label.configure(
                text="No passwords saved yet. Start by adding your first credential."
            )
            return
        report = self.password_health_service.analyze(self.vault_service.list_all_entries())
        self.empty_state_label.configure(
            text=(
                f"Security {report.score}/100 | Weak {report.weak_passwords} | "
                f"Duplicates {report.duplicate_passwords} | Old {report.old_passwords}"
            )
        )

    def toggle_password_visibility(self) -> None:
        self.show_password_value = not self.show_password_value
        self.password_entry.configure(show="" if self.show_password_value else "*")
        if self.icons.get("eye") and self.icons.get("eye-off"):
            self.eye_button.configure(
                image=self.icons["eye-off"] if self.show_password_value else self.icons["eye"]
            )

    def copy_password(self) -> None:
        password = self.password_entry.get()
        if not password:
            self.flash_error(self.password_entry)
            return
        self.clipboard_service.copy(password, scheduler=self)
        self.toast_manager.show("Password copied. Clears in 20 seconds.")

    def update_strength_bar(self, *args) -> None:
        strength = self.password_generator.evaluate_strength(self.password_entry.get())
        tone_to_color = {
            "empty": BORDER_COLOR,
            "weak": ERROR_COLOR,
            "medium": WARNING_COLOR,
            "strong": SUCCESS_COLOR,
        }
        color = tone_to_color[strength.tone]
        self.strength_bar.set(strength.progress)
        self.strength_bar.configure(progress_color=color)
        self.strength_label.configure(
            text=strength.label,
            text_color=MUTED_TEXT if strength.tone == "empty" else color,
        )

    def generate_password(self) -> None:
        self._insert_generated_password(PasswordGeneratorOptions())

    def open_generator_options(self) -> None:
        PasswordGeneratorDialog(self, self._insert_generated_password)

    def _insert_generated_password(self, options: PasswordGeneratorOptions) -> None:
        try:
            generated_password = self.password_generator.generate(options)
        except ValueError as error:
            self.toast_manager.show(str(error), is_error=True)
            return
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, generated_password)
        self.copy_password()

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
        self.password_var.set("")
        self._show_login_view()
        self.toast_manager.show(message)

    def save_password(self) -> None:
        if self.vault_service is None:
            return
        title = self.title_entry.get().strip()
        website = self.website_entry.get().strip()
        username = self.email_entry.get().strip()
        password = self.password_entry.get()
        validation = validate_credential_input(
            CredentialInput(
                title=title,
                website=website,
                username=username,
                password=password,
            )
        )

        if not validation["title"]:
            self.flash_error(self.title_entry)
        if not validation["website"]:
            self.flash_error(self.website_entry)
        if not validation["username"]:
            self.flash_error(self.email_entry)
        if not validation["password"]:
            self.flash_error(self.password_entry)
        if not all(validation.values()):
            self.toast_manager.show("Please fill all fields", is_error=True)
            return

        self.vault_service.save_entry(
            title=title,
            website=website,
            username=username,
            password=password,
            notes=self.notes_entry.get("1.0", "end-1c"),
            category=self.category_var.get(),
            tags=self.tags_entry.get().strip(),
            icon=self.icon_entry.get().strip(),
            favorite=self.favorite_var.get(),
        )
        self.toast_manager.show("Saved Securely")

        self.title_entry.delete(0, "end")
        self.website_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.tags_entry.delete(0, "end")
        self.icon_entry.delete(0, "end")
        self.notes_entry.delete("1.0", "end")
        self.favorite_var.set(False)
        self.password_var.set("")
        self.refresh_credential_count()

    def find_password(self) -> None:
        if self.vault_service is None:
            return
        website = self.website_entry.get().strip()
        if not website:
            self.flash_error(self.website_entry)
            self.toast_manager.show("Enter website to search", is_error=True)
            return

        matches = self.vault_service.search_entries(website)
        if not matches:
            self.toast_manager.show("No Saved Credentials", is_error=True)
            self.email_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            return
        credential = matches[0]

        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, credential.title)
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, credential.username)
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, credential.password)
        self.category_var.set(credential.category or "Personal")
        self.tags_entry.delete(0, "end")
        self.tags_entry.insert(0, credential.tags)
        self.icon_entry.delete(0, "end")
        self.icon_entry.insert(0, credential.icon)
        self.notes_entry.delete("1.0", "end")
        self.notes_entry.insert("1.0", credential.notes)
        self.favorite_var.set(credential.favorite)
        self.toast_manager.show(f"{len(matches)} matching entries")

    def flash_error(self, entry) -> None:
        flash_entry_error(entry, ERROR_COLOR, BORDER_COLOR)
