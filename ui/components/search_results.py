import customtkinter as ctk
from ui.theme import CORES, FONTES

class SearchResultsList(ctk.CTkScrollableFrame):
    def __init__(self, parent, callback_select, **kwargs):
        super().__init__(parent, height=200, fg_color=CORES["fundo_card"], border_width=1, border_color=CORES["glass_borda"], **kwargs)
        self.callback_select = callback_select
        self.items = []

    def atualizar_resultados(self, resultados):
        for widget in self.winfo_children():
            widget.destroy()
        
        if not resultados:
            ctk.CTkLabel(self, text="Nenhum resultado encontrado", font=FONTES["corpo"], text_color=CORES["texto_muted"]).pack(pady=10)
            return

        for texto in resultados:
            btn = ctk.CTkButton(
                self, 
                text=texto, 
                anchor="w", 
                fg_color="transparent", 
                text_color=CORES["texto_claro"],
                hover_color=CORES["destaque"],
                font=FONTES["corpo"],
                command=lambda t=texto: self.callback_select(t)
            )
            btn.pack(fill="x", pady=1)
