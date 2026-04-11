import customtkinter as ctk
from tkinter import messagebox, ttk
import datetime
from ui.theme import CORES, FONTES
from ui.components.glass_card import GlassCard

class AbaHistorico(ctk.CTkFrame):
    """Frame que exibe o histórico de eventos do sistema."""
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.carrinho = carrinho_controller
        self.app = app_controller

        self.setup_widgets()
        self.atualizar_historico()

    def setup_widgets(self):
        # Card Principal
        card = GlassCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Header do Card
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(header, text="🕒 Histórico de Atividades", font=FONTES["subtitulo"]).pack(side="left")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        ctk.CTkButton(
            actions, 
            text="Limpar Logs", 
            width=120,
            fg_color=CORES["cancelar"],
            hover_color=CORES["destaque_hover"],
            font=FONTES["botao"],
            command=self.apagar_historico
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            actions, 
            text="Atualizar", 
            width=120,
            fg_color=CORES["destaque"],
            hover_color=CORES["destaque_hover"],
            font=FONTES["botao"],
            command=self.atualizar_historico
        ).pack(side="right", padx=5)

        # Tabela (Treeview)
        cols = ('Data/Hora', 'Gaveta', 'Usuário', 'Ação', 'Resultado')
        self.tree_historico = ttk.Treeview(card, columns=cols, show='headings')
        
        for col in cols:
            self.tree_historico.heading(col, text=col)
            self.tree_historico.column(col, width=150)

        self.tree_historico.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    def atualizar_historico(self):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        
        eventos = self.carrinho.db.obter_historico(200) # Aumentado para 200 logs
        for ev in eventos:
            dt = ev.timestamp[:19].replace('T', ' ') if ev.timestamp else "N/A"
            status = "✅ Sucesso" if ev.sucesso else "❌ Falha"
            u = self.carrinho.db.obter_usuario_por_id(ev.usuario_id)
            nome_u = u.nome if u else ev.usuario_id
            self.tree_historico.insert('', 'end', values=(
                dt, f"Gaveta {ev.gaveta_id}", nome_u, ev.acao.upper(), status
            ))

    def apagar_historico(self):
        if messagebox.askyesno("Confirmar", "Deseja apagar TODO o histórico?"):
            try:
                self.carrinho.db.limpar_historico()
                self.atualizar_historico()
            except Exception as e:
                messagebox.showerror("Erro", str(e))