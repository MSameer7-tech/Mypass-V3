import customtkinter as ctk
from ui_legacy.design_system import themes, typography, spacing, radius
from ui_legacy.components import (
    Button, Label, TextField, PasswordField, SearchField, TextArea, Dropdown,
    Card, Badge, Divider, ProgressBar, PasswordStrengthIndicator,
    EmptyState, ToastManager, BaseDialog, Sidebar, Container, Checkbox, Radio
)

class PreviewApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=themes.DarkTheme.background)
        self.title("MyPass Component Explorer")
        self.geometry("1000x700")
        
        self.toast_manager = ToastManager(self)
        
        # Main layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Content Area
        self.content_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=spacing.L, pady=spacing.L)
        
        self._build_sidebar()
        self.show_page("Buttons")
        
    def _build_sidebar(self):
        Label(self.sidebar, text="Components", typography=typography.Headline).pack(anchor="w", padx=spacing.M, pady=spacing.L)
        
        pages = [
            "Buttons", "Inputs", "Labels", "Cards", "Dialogs", 
            "Badges", "Progress", "Empty States", "Icons", "Theme"
        ]
        
        for page in pages:
            Button(
                self.sidebar, 
                text=page, 
                variant="ghost", 
                command=lambda p=page: self.show_page(p)
            ).pack(fill="x", padx=spacing.M, pady=spacing.XS)
            
    def show_page(self, page_name: str):
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        Label(self.content_area, text=page_name, typography=typography.Display).pack(anchor="w", pady=(0, spacing.L))
        Divider(self.content_area).pack(fill="x", pady=(0, spacing.L))
        
        if page_name == "Buttons":
            self._render_buttons()
        elif page_name == "Inputs":
            self._render_inputs()
        elif page_name == "Labels":
            self._render_labels()
        elif page_name == "Cards":
            self._render_cards()
        elif page_name == "Dialogs":
            self._render_dialogs()
        elif page_name == "Badges":
            self._render_badges()
        elif page_name == "Progress":
            self._render_progress()
        elif page_name == "Empty States":
            self._render_empty_states()
        elif page_name == "Icons":
            self._render_icons()
        elif page_name == "Theme":
            self._render_theme()
            
    def _render_buttons(self):
        for variant in ["primary", "secondary", "ghost", "danger"]:
            row = Container(self.content_area)
            row.pack(fill="x", pady=spacing.S)
            Label(row, text=variant.capitalize(), typography=typography.BodyBold).pack(side="left", padx=(0, spacing.M))
            
            for size in ["small", "medium", "large"]:
                Button(row, text=size.capitalize(), variant=variant, size=size).pack(side="left", padx=spacing.XS)
                
        row = Container(self.content_area)
        row.pack(fill="x", pady=spacing.S)
        Label(row, text="With Icons", typography=typography.BodyBold).pack(side="left", padx=(0, spacing.M))
        Button(row, text="Add Item", icon="eye").pack(side="left", padx=spacing.XS)
        Button(row, text="Copy", icon="copy", variant="secondary").pack(side="left", padx=spacing.XS)

    def _render_inputs(self):
        states = ["normal", "focused", "error", "disabled"]
        
        Container(self.content_area).pack(pady=spacing.M)
        
        for state in states:
            row = Container(self.content_area)
            row.pack(fill="x", pady=spacing.S)
            
            TextField(row, label=f"TextField ({state})", placeholder="Type here...", state=state, error_message="Error msg" if state=="error" else None).pack(side="left", expand=True, padx=spacing.XS)
            PasswordField(row, label=f"PasswordField ({state})", placeholder="Secret...", state=state, allow_copy=True).pack(side="left", expand=True, padx=spacing.XS)
            
        row = Container(self.content_area)
        row.pack(fill="x", pady=spacing.L)
        SearchField(row, placeholder="Search vault...").pack(side="left", expand=True, padx=spacing.XS)
        
        row = Container(self.content_area)
        row.pack(fill="x", pady=spacing.S)
        Checkbox(row, text="Checkbox Unchecked").pack(side="left", padx=spacing.XS)
        Radio(row, text="Radio Option").pack(side="left", padx=spacing.XS)

    def _render_labels(self):
        for typo in [typography.Display, typography.Title, typography.Headline, typography.BodyBold, typography.Body, typography.Caption, typography.Tiny]:
            Label(self.content_area, text=f"Typography: {typo.name}", typography=typo).pack(anchor="w", pady=spacing.XS)
            
        Divider(self.content_area).pack(fill="x", pady=spacing.L)
        
        for variant in ["primary", "muted", "success", "danger", "warning"]:
            Label(self.content_area, text=f"Variant: {variant}", variant=variant).pack(anchor="w", pady=spacing.XS)

    def _render_cards(self):
        c1 = Card(self.content_area, padding=spacing.L)
        c1.pack(fill="x", pady=spacing.M)
        Label(c1.get_container(), text="Standard Card", typography=typography.Headline).pack()
        Label(c1.get_container(), text="Using surface color and border", variant="muted").pack()
        
        c2 = Card(self.content_area, padding=spacing.L)
        c2.pack(fill="x", pady=spacing.M)
        Label(c2.get_container(), text="Another Card", typography=typography.Headline).pack()
        Button(c2.get_container(), text="Action").pack(pady=spacing.M)

    def _render_dialogs(self):
        def show_dialog(title):
            d = BaseDialog(self, title=title, width=300, height=200)
            Label(d.body_frame, text="This is a dialog").pack(pady=spacing.M)
            d.add_standard_buttons("Confirm", d.destroy, d.destroy)
            
        Button(self.content_area, text="Open Standard Dialog", command=lambda: show_dialog("Test Dialog")).pack(anchor="w", pady=spacing.S)
        
        Button(self.content_area, text="Show Success Toast", command=lambda: self.toast_manager.show("Operation successful!")).pack(anchor="w", pady=spacing.S)
        Button(self.content_area, text="Show Error Toast", command=lambda: self.toast_manager.show("Operation failed!", is_error=True), variant="danger").pack(anchor="w", pady=spacing.S)

    def _render_badges(self):
        row = Container(self.content_area)
        row.pack(fill="x", pady=spacing.M)
        for variant in ["default", "success", "warning", "danger"]:
            Badge(row, text=variant.capitalize(), variant=variant).pack(side="left", padx=spacing.XS)

    def _render_progress(self):
        ProgressBar(self.content_area, progress=0.3).pack(fill="x", pady=spacing.M)
        ProgressBar(self.content_area, progress=0.7, variant="success").pack(fill="x", pady=spacing.M)
        
        ind = PasswordStrengthIndicator(self.content_area)
        ind.pack(fill="x", pady=spacing.M)
        ind.set_strength(2, "Fair")

    def _render_empty_states(self):
        EmptyState(
            self.content_area, 
            title="No Items Found", 
            message="Try adjusting your search filters.",
            action_text="Clear Filters",
            action_command=lambda: print("cleared")
        ).pack(expand=True, fill="both", pady=spacing.XL)

    def _render_icons(self):
        row = Container(self.content_area)
        row.pack(fill="x", pady=spacing.M)
        
        icons = ["eye", "eye-off", "copy", "search", "delete"]
        for icon in icons:
            # We can use buttons with ghost variant to show icons easily
            Button(row, text=icon, icon=icon, variant="ghost").pack(side="left", padx=spacing.XS)

    def _render_theme(self):
        def toggle_theme():
            current = themes.get_theme()
            new_theme = themes.LightTheme if current == themes.DarkTheme else themes.DarkTheme
            themes.ThemeManager.set_theme(new_theme)
            # Reconfigure root background manually as it's not a component
            self.configure(fg_color=new_theme.background)
            self.content_area.configure(fg_color="transparent")
            
        Button(self.content_area, text="Toggle Light/Dark Theme", command=toggle_theme).pack(anchor="w", pady=spacing.M)
        
        Divider(self.content_area).pack(fill="x", pady=spacing.L)
        
        Label(self.content_area, text="Theme Tokens", typography=typography.Headline).pack(anchor="w", pady=spacing.S)
        theme = themes.get_theme()
        
        # Mini palette preview
        for name, color in [("Background", theme.background), ("Surface", theme.surface), ("Accent", theme.accent), ("Danger", theme.danger)]:
            row = Container(self.content_area)
            row.pack(fill="x", pady=spacing.XS)
            color_box = ctk.CTkFrame(row, fg_color=color, width=24, height=24, corner_radius=4)
            color_box.pack(side="left")
            Label(row, text=f"{name}: {color}").pack(side="left", padx=spacing.M)

if __name__ == "__main__":
    app = PreviewApp()
    app.mainloop()
