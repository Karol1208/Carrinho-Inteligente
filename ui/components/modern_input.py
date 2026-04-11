import customtkinter as ctk
from ui.theme import Theme

class ModernInput(ctk.CTkEntry):
    """
    Entrada de texto estilizada usando o Theme Manager.
    """
    def __init__(self, master, placeholder_text="", **kwargs):
        super().__init__(
            master=master,
            placeholder_text=placeholder_text,
            border_width=1,
            corner_radius=8,
            height=45,
            justify="center",
            **kwargs
        )
        Theme.apply_input_style(self)
