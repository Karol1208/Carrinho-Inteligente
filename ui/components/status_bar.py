import customtkinter as ctk
from ui.theme import CORES, FONTES
from PIL import Image

class StatusBar(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=35, corner_radius=0, fg_color=CORES["fundo_secundario"], **kwargs)
        
        self.lbl_status = ctk.CTkLabel(self, text="  ● Sistema Operacional", font=FONTES["corpo"], text_color=CORES["sucesso"])
        self.lbl_status.pack(side="left", padx=20)
        
        self.lbl_hw = ctk.CTkLabel(self, text="📡 Leitor RFID: ONLINE", font=FONTES["corpo"], text_color=CORES["texto_claro"])
        self.lbl_hw.pack(side="left", padx=20)
        
        self.lbl_cpu = ctk.CTkLabel(self, text="CPU: 12% | RAM: 450MB", font=FONTES["corpo"], text_color=CORES["texto_muted"])
        self.lbl_cpu.pack(side="right", padx=20)

    def set_hw_status(self, online=True):
        if online:
            self.lbl_hw.configure(text="📡 Leitor RFID: ONLINE", text_color=CORES["sucesso"])
        else:
            self.lbl_hw.configure(text="📡 Leitor RFID: OFFLINE", text_color=CORES["cancelar"])
