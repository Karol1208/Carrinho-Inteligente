import customtkinter as ctk
from ui.theme import CORES

class GlassCard(ctk.CTkFrame):
    """
    Componente que simula o efeito Glassmorphism.
    """
    def __init__(self, master, **kwargs):
        super().__init__(
            master, 
            fg_color=CORES["fundo_card"],
            border_color=CORES["glass_borda"],
            border_width=1,
            corner_radius=15,
            **kwargs
        )
