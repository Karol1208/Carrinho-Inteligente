import customtkinter as ctk
from tkinter import messagebox, ttk
import datetime
from ui.theme import CORES, FONTES
from models.entities import Peca
from ui.components.glass_card import GlassCard

class AbaInventario(ctk.CTkFrame):
    """Frame que gerencia o inventário de peças e as pendências."""
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.carrinho = carrinho_controller
        self.app = app_controller

        self.setup_widgets()
        self.atualizar_lista_pecas()
        self.atualizar_combo_usuarios_pendencias()
        self.atualizar_pendencias_usuario()

    def setup_widgets(self):
        # Container com Scroll
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Card de Ações Rápidas
        acoes_card = GlassCard(self.scroll_container)
        acoes_card.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(acoes_card, text="📦 Gestão de Inventário", font=FONTES["subtitulo"]).pack(side="left", padx=20, pady=20)
        
        ctk.CTkButton(
            acoes_card,
            text="+ ADICIONAR / ATUALIZAR PEÇA",
            fg_color=CORES["sucesso"],
            hover_color="#27ae60",
            font=FONTES["botao"],
            height=40,
            command=self.mostrar_popup_cadastro_peca
        ).pack(side="right", padx=20, pady=20)

        # 2. Card da Tabela de Peças
        inventory_card = GlassCard(self.scroll_container)
        inventory_card.pack(fill="x", padx=10, pady=10)

        toolbar_inv = ctk.CTkFrame(inventory_card, fg_color="transparent")
        toolbar_inv.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(toolbar_inv, text="Catálogo de Ferramentas", font=FONTES["corpo"]).pack(side="left")

        ctk.CTkButton(toolbar_inv, text="🗑 Remover", width=100, fg_color=CORES["cancelar"], command=self.remover_peca_selecionada).pack(side="right", padx=5)
        ctk.CTkButton(toolbar_inv, text="🔄 Atualizar", width=100, fg_color=CORES["destaque"], command=self.atualizar_lista_pecas).pack(side="right", padx=5)

        cols_inv = ('ID', 'Nome', 'Categoria', 'Tipo', 'Gaveta', 'Qtd')
        self.tree_pecas = ttk.Treeview(inventory_card, columns=cols_inv, show='headings', height=8)
        for col in cols_inv:
            self.tree_pecas.heading(col, text=col)
            self.tree_pecas.column(col, width=100)
        self.tree_pecas.pack(fill='both', expand=True, padx=20, pady=20)

        # 3. Card de Pendências por Usuário
        pendencias_card = GlassCard(self.scroll_container)
        pendencias_card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(pendencias_card, text="⚠️ Pendências por Usuário", font=FONTES["subtitulo"]).pack(anchor="w", padx=20, pady=(20, 10))

        filter_row = ctk.CTkFrame(pendencias_card, fg_color="transparent")
        filter_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(filter_row, text="Selecionar Colaborador:", font=FONTES["corpo"]).pack(side="left", padx=(0, 10))
        self.combo_usuario_pendencias = ctk.CTkComboBox(
            filter_row, 
            width=300, 
            command=lambda _: self.atualizar_pendencias_usuario()
        )
        self.combo_usuario_pendencias.pack(side="left")

        cols_pend = ('Peça', 'Retirada', 'Devolvida', 'Pendente', 'Data', 'Status')
        self.tree_pendencias = ttk.Treeview(pendencias_card, columns=cols_pend, show='headings', height=6)
        for col in cols_pend:
            self.tree_pendencias.heading(col, text=col)
            self.tree_pendencias.column(col, width=100)
        self.tree_pendencias.pack(fill='both', expand=True, padx=20, pady=20)

    def atualizar_lista_pecas(self):
        for item in self.tree_pecas.get_children(): self.tree_pecas.delete(item)
        pecas = self.carrinho.listar_todas_pecas()
        for peca in pecas:
            self.tree_pecas.insert('', 'end', values=(
                peca.id, peca.nome, peca.categoria, peca.tipo, peca.gaveta_id, peca.quantidade_disponivel
            ))

    def remover_peca_selecionada(self):
        selection = self.tree_pecas.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma peça!")
            return
        item = self.tree_pecas.item(selection[0])
        pid, nome = item['values'][0], item['values'][1]
        if messagebox.askyesno("Confirmar", f"Desativar peça '{nome}'?"):
            self.carrinho.db.remover_peca(pid)
            self.atualizar_lista_pecas()

    def atualizar_combo_usuarios_pendencias(self):
        usuarios = self.carrinho.db.listar_usuarios()
        nomes = [u.nome for u in usuarios if (not hasattr(u, 'ativo') or u.ativo)]
        self.combo_usuario_pendencias.configure(values=nomes)
        if nomes: self.combo_usuario_pendencias.set(nomes[0])

    def atualizar_pendencias_usuario(self):
        nome = self.combo_usuario_pendencias.get()
        if not nome: return
        usuarios = self.carrinho.db.listar_usuarios()
        u = next((u for u in usuarios if u.nome == nome), None)
        if not u: return

        for item in self.tree_pendencias.get_children(): self.tree_pendencias.delete(item)
        for ret in self.carrinho.obter_pecas_pendentes_usuario(u.id):
            peca = self.carrinho.db.obter_peca_por_id(ret.peca_id)
            nome_p = peca.nome if peca else f"ID {ret.peca_id}"
            pend = ret.quantidade_retirada - ret.quantidade_devolvida
            dt = ret.timestamp_retirada[:16] if ret.timestamp_retirada else "N/A"
            self.tree_pendencias.insert('', 'end', values=(nome_p, ret.quantidade_retirada, ret.quantidade_devolvida, pend, dt, ret.status))

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
                    quantidade_disponivel=int(self.entries["Qtd Inicial"].get())
                )
                if self.carrinho.adicionar_peca(p):
                    messagebox.showinfo("Sucesso", "Peça cadastrada!")
                    popup.destroy()
                    self.atualizar_lista_pecas()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        btn_f = ctk.CTkFrame(popup, fg_color="transparent")
        btn_f.pack(pady=30)
        ctk.CTkButton(btn_f, text="SALVAR", fg_color=CORES["sucesso"], command=salvar).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="CANCELAR", fg_color=CORES["cancelar"], command=popup.destroy).pack(side="left", padx=10)
