import customtkinter as ctk
from tkinter import messagebox
from ui.theme import CORES, FONTES
from ui.components.glass_card import GlassCard
from ui.components.tabela_pro import TabelaPRO


class AbaHistorico(ctk.CTkFrame):
    """Frame que exibe o histórico de eventos do sistema."""

    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.carrinho = carrinho_controller
        self.app = app_controller

        self.setup_widgets()
        self.atualizar_historico()

    # ─────────────────────────────────────────────────────
    #  Layout
    # ─────────────────────────────────────────────────────
    def setup_widgets(self):
        card = GlassCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            header, text="🕒 Histórico de Atividades", font=FONTES["subtitulo"]
        ).pack(side="left")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        ctk.CTkButton(
            actions,
            text="Limpar Logs",
            width=120,
            fg_color=CORES["cancelar"],
            hover_color=CORES["destaque_hover"],
            font=FONTES["botao"],
            command=self.apagar_historico,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            actions,
            text="Atualizar",
            width=120,
            fg_color=CORES["destaque"],
            hover_color=CORES["destaque_hover"],
            font=FONTES["botao"],
            command=self.atualizar_historico,
        ).pack(side="right", padx=5)

        # TabelaPRO — coluna "Resultado" como badge (índice 4)
        self.tabela_historico = TabelaPRO(
            card,
            columns=["Data / Hora", "Gaveta", "Usuário", "Ação", "Resultado"],
            col_widths=[2, 1, 2, 2, 1],
            status_col=4,      # coluna Resultado → badge colorido
            show_actions=False,
        )
        self.tabela_historico.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ─────────────────────────────────────────────────────
    #  Lógica de dados
    # ─────────────────────────────────────────────────────
    def atualizar_historico(self):
        eventos = self.carrinho.db.obter_historico(200)
        data = []
        for ev in eventos:
            dt     = ev.timestamp[:19].replace("T", " ") if ev.timestamp else "N/A"
            status = "sucesso" if ev.sucesso else "falha"
            u      = self.carrinho.db.obter_usuario_por_id(ev.usuario_id)
            nome_u = u.nome if u else str(ev.usuario_id)
            data.append([dt, f"Gaveta {ev.gaveta_id}", nome_u, ev.acao.upper(), status])

        self.tabela_historico.carregar(data)

    def apagar_historico(self):
        if messagebox.askyesno("Confirmar", "Deseja apagar TODO o histórico?"):
            try:
                self.carrinho.db.limpar_historico()
                self.atualizar_historico()
            except Exception as e:
                messagebox.showerror("Erro", str(e))