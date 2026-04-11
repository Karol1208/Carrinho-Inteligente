import customtkinter as ctk
from ui.theme import Theme

class PrimaryButton(ctk.CTkButton):
    """
    Botão estilizado com a identidade visual premium usando o Theme Manager.
    """
    def __init__(self, master, text, command=None, style="primary", **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            corner_radius=8,
            height=40,
            **kwargs
        )
        Theme.apply_button_style(self, style=style)
