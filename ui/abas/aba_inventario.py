import customtkinter as ctk
from tkinter import messagebox
from ui.theme import CORES, FONTES
from models.entities import Peca
from ui.components.glass_card import GlassCard
from ui.components.tabela_pro import TabelaPRO


class AbaInventario(ctk.CTkFrame):
    """Frame que gerencia o inventário de peças e as pendências."""

    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.carrinho = carrinho_controller
        self.app = app_controller
        self._peca_selecionada = None  # row_data da linha selecionada

        self.setup_widgets()
        self.atualizar_lista_pecas()
        self.atualizar_combo_usuarios_pendencias()
        self.atualizar_pendencias_usuario()

    # ─────────────────────────────────────────────────────
    #  Layout
    # ─────────────────────────────────────────────────────
    def setup_widgets(self):
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ── 1. Card de ações rápidas ──────────────────────
        acoes_card = GlassCard(self.scroll_container)
        acoes_card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            acoes_card, text="📦 Gestão de Inventário", font=FONTES["subtitulo"]
        ).pack(side="left", padx=20, pady=20)

        ctk.CTkButton(
            acoes_card,
            text="+ ADICIONAR / ATUALIZAR PEÇA",
            fg_color=CORES["sucesso"],
            hover_color="#27ae60",
            font=FONTES["botao"],
            height=40,
            command=self.mostrar_popup_cadastro_peca,
        ).pack(side="right", padx=20, pady=20)

        # ── 2. Card da tabela de peças ────────────────────
        inventory_card = GlassCard(self.scroll_container)
        inventory_card.pack(fill="x", padx=10, pady=10)

        toolbar_inv = ctk.CTkFrame(inventory_card, fg_color="transparent")
        toolbar_inv.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            toolbar_inv, text="Catálogo de Ferramentas", font=FONTES["corpo"]
        ).pack(side="left")

        ctk.CTkButton(
            toolbar_inv, text="🗑 Remover", width=100,
            fg_color=CORES["cancelar"],
            command=self._remover_selecionada,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            toolbar_inv, text="🔄 Atualizar", width=100,
            fg_color=CORES["destaque"],
            command=self.atualizar_lista_pecas,
        ).pack(side="right", padx=5)

        # TabelaPRO — peças (sem botões de ação inline; remoção via toolbar)
        self.tabela_pecas = TabelaPRO(
            inventory_card,
            columns=["ID", "Nome", "Categoria", "Tipo", "Gaveta", "Qtd"],
            col_widths=[1, 3, 2, 2, 1, 1],
            on_select=self._on_peca_select,
            show_actions=False,
        )
        self.tabela_pecas.pack(fill="both", expand=True, padx=20, pady=20)

        # ── 3. Card de pendências por usuário ─────────────
        pendencias_card = GlassCard(self.scroll_container)
        pendencias_card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            pendencias_card,
            text="⚠️ Pendências por Usuário",
            font=FONTES["subtitulo"],
        ).pack(anchor="w", padx=20, pady=(20, 10))

        filter_row = ctk.CTkFrame(pendencias_card, fg_color="transparent")
        filter_row.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            filter_row, text="Selecionar Colaborador:", font=FONTES["corpo"]
        ).pack(side="left", padx=(0, 10))

        self.combo_usuario_pendencias = ctk.CTkComboBox(
            filter_row,
            width=300,
            command=lambda _: self.atualizar_pendencias_usuario(),
        )
        self.combo_usuario_pendencias.pack(side="left")

        # TabelaPRO — pendências (coluna Status como badge)
        self.tabela_pendencias = TabelaPRO(
            pendencias_card,
            columns=["Peça", "Retirada", "Devolvida", "Pendente", "Data", "Status"],
            col_widths=[3, 1, 1, 1, 2, 2],
            status_col=5,          # coluna "Status" → badge
            show_actions=False,
        )
        self.tabela_pendencias.pack(fill="both", expand=True, padx=20, pady=20)

    # ─────────────────────────────────────────────────────
    #  Callbacks de seleção
    # ─────────────────────────────────────────────────────
    def _on_peca_select(self, row_data: list):
        """Guarda a linha selecionada para uso no botão Remover."""
        self._peca_selecionada = row_data

    # ─────────────────────────────────────────────────────
    #  Lógica de dados
    # ─────────────────────────────────────────────────────
    def atualizar_lista_pecas(self):
        pecas = self.carrinho.listar_todas_pecas()
        data = [
            [p.id, p.nome, p.categoria, p.tipo, p.gaveta_id, p.quantidade_disponivel]
            for p in pecas
        ]
        self.tabela_pecas.carregar(data)
        self._peca_selecionada = None

    def _remover_selecionada(self):
        if not self._peca_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma peça clicando na linha.")
            return
        pid, nome = self._peca_selecionada[0], self._peca_selecionada[1]
        if messagebox.askyesno("Confirmar", f"Desativar peça '{nome}'?"):
            self.carrinho.db.remover_peca(pid)
            self.atualizar_lista_pecas()

    def atualizar_combo_usuarios_pendencias(self):
        usuarios = self.carrinho.db.listar_usuarios()
        nomes = [u.nome for u in usuarios if (not hasattr(u, "ativo") or u.ativo)]
        self.combo_usuario_pendencias.configure(values=nomes)
        if nomes:
            self.combo_usuario_pendencias.set(nomes[0])

    def atualizar_pendencias_usuario(self):
        nome = self.combo_usuario_pendencias.get()
        if not nome:
            return
        usuarios = self.carrinho.db.listar_usuarios()
        u = next((u for u in usuarios if u.nome == nome), None)
        if not u:
            return

        data = []
        for ret in self.carrinho.obter_pecas_pendentes_usuario(u.id):
            peca  = self.carrinho.db.obter_peca_por_id(ret.peca_id)
            nome_p = peca.nome if peca else f"ID {ret.peca_id}"
            pend  = ret.quantidade_retirada - ret.quantidade_devolvida
            dt    = ret.timestamp_retirada[:16] if ret.timestamp_retirada else "N/A"
            data.append([nome_p, ret.quantidade_retirada, ret.quantidade_devolvida, pend, dt, ret.status])

        self.tabela_pendencias.carregar(data)

    # ─────────────────────────────────────────────────────
    #  Popup de cadastro
    # ─────────────────────────────────────────────────────
    def mostrar_popup_cadastro_peca(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Cadastro de Peça")
        popup.geometry("500x600")
        popup.configure(fg_color=CORES["fundo_principal"])
        popup.grab_set()

        ctk.CTkLabel(popup, text="DADOS DA FERRAMENTA", font=FONTES["subtitulo"]).pack(pady=20)

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(padx=40, pady=10, fill="both")

        campos = ["Nome", "Categoria", "Descrição", "Tipo", "Gaveta ID", "Qtd Inicial"]
        self.entries = {}
        for campo in campos:
            ctk.CTkLabel(form, text=campo, font=FONTES["corpo"]).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(form, height=40)
            entry.pack(fill="x", pady=(5, 0))
            self.entries[campo] = entry

        def salvar():
            try:
                p = Peca(
                    id=0,
                    nome=self.entries["Nome"].get(),
                    categoria=self.entries["Categoria"].get(),
                    descricao=self.entries["Descrição"].get(),
                    tipo=self.entries["Tipo"].get(),
                    gaveta_id=int(self.entries["Gaveta ID"].get()),
                    quantidade_disponivel=int(self.entries["Qtd Inicial"].get()),
                )
                if self.carrinho.adicionar_peca(p):
                    messagebox.showinfo("Sucesso", "Peça cadastrada!")
                    popup.destroy()
                    self.atualizar_lista_pecas()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        btn_f = ctk.CTkFrame(popup, fg_color="transparent")
        btn_f.pack(pady=30)
        ctk.CTkButton(btn_f, text="SALVAR",   fg_color=CORES["sucesso"], command=salvar).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="CANCELAR", fg_color=CORES["cancelar"], command=popup.destroy).pack(side="left", padx=10)