import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from ui.theme import CORES, FONTES
from models.entities import Peca

class AbaInventario(ttk.Frame):
    """Frame que gerencia o inventário de peças e as pendências."""
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent)
        self.carrinho = carrinho_controller
        self.app = app_controller

        self.setup_widgets()
        self.atualizar_lista_pecas()
        self.atualizar_combo_usuarios_pendencias()
        self.atualizar_pendencias_usuario()

    def setup_widgets(self):
        style = ttk.Style()
        style.configure("Sucesso.TButton",
                        font=FONTES["botao"],
                        background=CORES["sucesso"],
                        foreground=CORES["texto_claro"])
        style.map("Sucesso.TButton",
                  background=[('active', '#27ae60')])
        cor_vermelha = CORES.get("cancelar", "#e74c3c")
        cor_vermelha_active = CORES.get("cancelar_active", "#c0392b")
        style.configure("Remover.TButton",
                        font=FONTES["botao"],
                        background=cor_vermelha,
                        foreground=CORES["texto_claro"])
        style.map("Remover.TButton",
                  background=[('active', cor_vermelha_active)])

        frame_acoes = ttk.LabelFrame(self, text="Ações", padding=10)
        frame_acoes.pack(fill='x', padx=10, pady=5)
        ttk.Button(
            frame_acoes, 
            text="Adicionar/Atualizar Peça", 
            command=self.mostrar_popup_cadastro_peca,
            style="Sucesso.TButton"
        ).pack(pady=10)

        frame_lista_pecas = ttk.LabelFrame(self, text="Todas as Peças", padding=10)
        frame_lista_pecas.pack(fill='both', expand=True, padx=10, pady=5)

        columns_pecas = ('ID', 'Nome', 'Categoria', 'Descrição', 'Tipo', 'Gaveta', 'Qtd Disponível')
        self.tree_pecas = ttk.Treeview(frame_lista_pecas, columns=columns_pecas, show='headings', height=10)
        for col in columns_pecas:
            self.tree_pecas.heading(col, text=col)
            self.tree_pecas.column(col, width=120)
        
        scrollbar_pecas = ttk.Scrollbar(frame_lista_pecas, orient='vertical', command=self.tree_pecas.yview)
        self.tree_pecas.configure(yscrollcommand=scrollbar_pecas.set)
        self.tree_pecas.pack(side='left', fill='both', expand=True)
        scrollbar_pecas.pack(side='right', fill='y')
        
        frame_botoes_pecas = ttk.Frame(frame_lista_pecas)
        frame_botoes_pecas.pack(fill='x', pady=5)

        ttk.Button(
            frame_botoes_pecas, 
            text="Atualizar Lista", 
            command=self.atualizar_lista_pecas,
            style="Sucesso.TButton"
        ).pack(side='left', padx=5)
        
        ttk.Button(
            frame_botoes_pecas, 
            text="Remover Selecionada", 
            command=self.remover_peca_selecionada,
            style="Remover.TButton"
        ).pack(side='left', padx=5)

        frame_pendencias = ttk.LabelFrame(self, text="Pendências de Peças por Usuário", padding=10)
        frame_pendencias.pack(fill='both', expand=True, padx=10, pady=5)

        ttk.Label(frame_pendencias, text="Selecione Usuário:", font=FONTES["subtitulo"]).pack(anchor='w', padx=5, pady=5)
        self.combo_usuario_pendencias = ttk.Combobox(frame_pendencias, width=30, font=FONTES["corpo"])
        self.combo_usuario_pendencias.pack(anchor='w', padx=5, pady=5)
        self.combo_usuario_pendencias.bind('<<ComboboxSelected>>', self.atualizar_pendencias_usuario)

        columns_pend = ('Peça', 'Qtd Retirada', 'Qtd Devolvida', 'Pendente', 'Data Retirada', 'Status')
        self.tree_pendencias = ttk.Treeview(frame_pendencias, columns=columns_pend, show='headings', height=8)
        for col in columns_pend:
            self.tree_pendencias.heading(col, text=col)
            self.tree_pendencias.column(col, width=120)

        scrollbar_pend = ttk.Scrollbar(frame_pendencias, orient='vertical', command=self.tree_pendencias.yview)
        self.tree_pendencias.configure(yscrollcommand=scrollbar_pend.set)
        self.tree_pendencias.pack(side='left', fill='both', expand=True, pady=5)
        scrollbar_pend.pack(side='right', fill='y')

    def atualizar_lista_pecas(self):
        for item in self.tree_pecas.get_children():
            self.tree_pecas.delete(item)
        pecas = self.carrinho.listar_todas_pecas()
        for peca in pecas:
            desc_short = peca.descricao[:30] + '...' if len(peca.descricao) > 30 else peca.descricao
            self.tree_pecas.insert('', 'end', values=(
                peca.id, peca.nome, peca.categoria, desc_short, peca.tipo, peca.gaveta_id, peca.quantidade_disponivel
            ))

    def remover_peca_selecionada(self):
        """Desativa a peça selecionada no Treeview."""
        selection = self.tree_pecas.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma peça da lista para apagar.")
            return

        item = self.tree_pecas.item(selection[0])
        peca_id = item['values'][0]
        nome_peca = item['values'][1]

        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja apagar a peça '{nome_peca}'?\n\nEsta ação apenas a desativará do sistema.",
            icon='warning'
        )

        if confirmar:
            try:
                self.carrinho.db.remover_peca(peca_id)
                messagebox.showinfo("Sucesso", f"A peça '{nome_peca}' foi removida (desativada) com sucesso.")
                self.atualizar_lista_pecas()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível remover a peça: {e}")

    def atualizar_combo_usuarios_pendencias(self):
        usuarios = self.carrinho.db.listar_usuarios()
        nomes_usuarios = [u.nome for u in usuarios if hasattr(u, 'ativo') and u.ativo]
        self.combo_usuario_pendencias['values'] = nomes_usuarios
        if nomes_usuarios:
            self.combo_usuario_pendencias.set(nomes_usuarios[0])

    def atualizar_pendencias_usuario(self, event=None):
        nome_usuario = self.combo_usuario_pendencias.get()
        if not nome_usuario: return

        usuarios = self.carrinho.db.listar_usuarios()
        usuario = next((u for u in usuarios if u.nome == nome_usuario and (not hasattr(u, 'ativo') or u.ativo)), None)
        if not usuario: return

        for item in self.tree_pendencias.get_children():
            self.tree_pendencias.delete(item)

        retiradas = self.carrinho.obter_pecas_pendentes_usuario(usuario.id)
        for ret in retiradas:
            peca = self.carrinho.db.obter_peca_por_id(ret.peca_id)
            nome_peca = peca.nome if peca else f"Peça ID {ret.peca_id}"
            pendente = ret.quantidade_retirada - ret.quantidade_devolvida
            try:
                data_ret = datetime.datetime.fromisoformat(ret.timestamp_retirada).strftime("%d/%m/%Y %H:%M")
            except Exception:
                data_ret = ret.timestamp_retirada or "N/A"
            self.tree_pendencias.insert('', 'end', values=(
                nome_peca, ret.quantidade_retirada, ret.quantidade_devolvida, pendente, data_ret, ret.status
            ))

    def mostrar_popup_cadastro_peca(self):
        popup = tk.Toplevel(self.app.root)
        popup.title("Adicionar/Atualizar Peça")
        popup.geometry("450x480")
        popup.resizable(False, False)
        popup.transient(self.app.root)
        popup.grab_set()
        popup.configure(bg=CORES["fundo_secundario"])

        tk.Label(popup, text="ADICIONAR/ATUALIZAR PEÇA", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(20, 20))

        form_frame = tk.Frame(popup, bg=CORES["fundo_secundario"])
        form_frame.pack(padx=30, pady=10)

        campos = ["Nome:", "Categoria:", "Descrição:", "Tipo:", "Gaveta ID (1-5):", "Quantidade Disponível:"]
        entries = {}

        for i, campo in enumerate(campos):
            lbl = tk.Label(form_frame, text=campo, font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"])
            lbl.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            entry = ttk.Entry(form_frame, font=FONTES["corpo"], width=30)
            entry.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            entries[campo] = entry
        
        entries["Nome:"].focus()

        def salvar_nova_peca():
            try:
                nome = entries["Nome:"].get().strip()
                categoria = entries["Categoria:"].get().strip()
                descricao = entries["Descrição:"].get().strip()
                tipo = entries["Tipo:"].get().strip()
                gaveta_id = int(entries["Gaveta ID (1-5):"].get().strip())
                qtd = int(entries["Quantidade Disponível:"].get().strip())
                if not nome or not (1 <= gaveta_id <= 5) or qtd < 0:
                    raise ValueError("Campos obrigatórios inválidos")
            except ValueError:
                messagebox.showerror("Erro de Validação", "Preencha os campos corretamente!\n- Nome é obrigatório.\n- Gaveta deve ser um número de 1 a 5.\n- Quantidade não pode ser negativa.", parent=popup)
                return

            peca = Peca(id=0, nome=nome, categoria=categoria, descricao=descricao, tipo=tipo, gaveta_id=gaveta_id, quantidade_disponivel=qtd)
            if self.carrinho.adicionar_peca(peca):
                messagebox.showinfo("Sucesso", f"Peça '{nome}' cadastrada com sucesso!", parent=popup)
                popup.destroy()
                self.atualizar_lista_pecas()
            else:
                messagebox.showerror("Erro de Sistema", "Falha ao cadastrar a peça. Verifique os logs.", parent=popup)

        frame_botoes = tk.Frame(popup, bg=CORES["fundo_secundario"])
        frame_botoes.pack(pady=20)
        
        btn_salvar = ttk.Button(frame_botoes, text="Salvar Peça", style="Sucesso.TButton", command=salvar_nova_peca)
        btn_salvar.pack(side="left", padx=10)
        
        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", style="Remover.TButton", command=popup.destroy)
        btn_cancelar.pack(side="left", padx=10)