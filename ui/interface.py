# Em ui/interface.py (VERSÃO ATUALIZADA COM POP-UPS E RESTR IÇÕES)

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import logging
import sqlite3
from PIL import Image, ImageTk

from core.cart import CarrinhoInteligenteAvancado
from models.entities import Peca, UsuarioCartao
from ui.painelMonitoramento import PainelMonitoramento
from ui.theme import CORES, FONTES


class InterfaceGraficaCarrinho:
    def __init__(self, carrinho: CarrinhoInteligenteAvancado = None):
        self.carrinho = carrinho if carrinho else CarrinhoInteligenteAvancado()
        self.root = tk.Tk()
        self.root.title("CRDF - Controle de Retirada e Devolução de Ferramentas")
        self.root.geometry("1280x720")
        self.root.minsize(1100, 700)
        self.root.configure(bg=CORES["fundo_widget"])
        
        self.usuario_atual = None
        self.frames_conteudo = {}
        self.botoes_sidebar = {}

        self.setup_estilos_ttk()
        self.setup_interface_principal()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.atualizar_status_periodico()

    def setup_estilos_ttk(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview",
                        background=CORES["fundo_widget"],
                        foreground=CORES["texto_escuro"],
                        rowheight=28,
                        fieldbackground=CORES["fundo_widget"],
                        font=FONTES["corpo"])
        style.map('Treeview', background=[('selected', CORES["destaque"])])

        style.configure("Treeview.Heading",
                        background=CORES["fundo_secundario"],
                        foreground=CORES["texto_claro"],
                        font=FONTES["botao"],
                        padding=(10, 10))
        
        style.configure('TLabel', font=FONTES["corpo"], background=CORES["fundo_widget"], foreground=CORES["texto_escuro"])
        style.configure('TButton', font=FONTES["botao"], padding=(10, 5))
        style.configure('TEntry', font=FONTES["corpo"])
        style.configure('LabelFrame.TLabel', font=FONTES["subtitulo"], background=CORES["fundo_widget"], foreground=CORES["texto_escuro"])

    def setup_interface_principal(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.criar_cabecalho()
        self.criar_sidebar()

        self.frame_conteudo_principal = tk.Frame(self.root, bg=CORES["fundo_widget"])
        self.frame_conteudo_principal.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.frame_conteudo_principal.grid_rowconfigure(0, weight=1)
        self.frame_conteudo_principal.grid_columnconfigure(0, weight=1)

        self.frames_conteudo["retirada"] = self.setup_aba_principal(self.frame_conteudo_principal)
        self.frames_conteudo["usuarios"] = self.setup_aba_usuarios(self.frame_conteudo_principal)
        self.frames_conteudo["historico"] = self.setup_aba_historico(self.frame_conteudo_principal)
        self.frames_conteudo["inventario"] = self.setup_aba_inventario(self.frame_conteudo_principal)
        
        self.mostrar_frame("retirada")

    def criar_cabecalho(self):
        header = tk.Frame(self.root, bg=CORES["fundo_secundario"], height=60)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.pack_propagate(False)

        try:
            self.logo_senai_header_img = ImageTk.PhotoImage(Image.open("logo_senai.png").resize((120, 40), Image.LANCZOS))
            tk.Label(header, image=self.logo_senai_header_img, bg=CORES["fundo_secundario"]).pack(side="left", padx=20)
        except Exception as e:
            tk.Label(header, text="SENAI", font=FONTES["titulo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(side="left", padx=20)
            logging.warning(f"Não foi possível carregar 'logo_senai.png': {e}")

        self.label_usuario_header = tk.Label(header, text="Nenhum usuário logado", font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"])
        self.label_usuario_header.pack(side="right", padx=20)

    def criar_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=CORES["fundo_secundario"], width=250)
        self.sidebar.grid(row=1, column=0, sticky="nsw")
        self.sidebar.pack_propagate(False)
        
        botoes_nav = {
            "retirada": "Painel de Retirada",
            "inventario": "Inventário",
            "usuarios": "Gerenciar Usuários",
            "historico": "Histórico"
        }

        for nome, texto in botoes_nav.items():
            btn = tk.Button(self.sidebar, text=texto, font=FONTES["botao"], bg=CORES["fundo_secundario"], 
                            fg=CORES["texto_claro"], relief="flat", anchor="w", padx=20, pady=15,
                            activebackground=CORES["destaque"], activeforeground=CORES["texto_claro"],
                            command=lambda f=nome: self.mostrar_frame(f))
            btn.pack(fill="x")
            self.botoes_sidebar[nome] = btn
            
        btn_monitor = tk.Button(self.sidebar, text="Monitor de Gavetas", font=FONTES["botao"], 
                                bg=CORES["fundo_secundario"], fg=CORES["alerta"], relief="flat", 
                                anchor="w", padx=20, pady=15, activebackground=CORES["destaque"],
                                activeforeground=CORES["texto_claro"], command=self.abrir_painel_monitoramento)
        btn_monitor.pack(fill="x", side="bottom", pady=(0, 20))
        self.botoes_sidebar["monitor"] = btn_monitor
        
    def mostrar_frame(self, nome_frame):
        for frame in self.frames_conteudo.values():
            frame.grid_remove()
        
        frame_ativo = self.frames_conteudo[nome_frame]
        frame_ativo.grid(row=0, column=0, sticky="nsew")
        
        for nome, btn in self.botoes_sidebar.items():
            if nome != 'monitor':
                btn.config(bg=CORES["fundo_secundario"])
        
        if nome_frame in self.botoes_sidebar:
            self.botoes_sidebar[nome_frame].config(bg=CORES["destaque"])

    def configurar_acesso_por_perfil(self, perfil):
        if self.usuario_atual:
            self.label_usuario_header.config(text=f"Bem-vindo, {self.usuario_atual.nome} ({self.usuario_atual.cargo}) - Perfil: {self.usuario_atual.perfil}", fg=CORES["texto_claro"])
        
        if perfil == "admin":
            # Admin vê tudo
            for nome, btn in self.botoes_sidebar.items():
                if nome != 'monitor':
                    btn.pack(fill="x")
            self.botoes_sidebar["monitor"].pack(fill="x", side="bottom", pady=(0, 20))
        elif perfil == "aluno":
            # Aluno só vê "retirada" (sem inventário, usuários ou histórico)
            for nome, btn in self.botoes_sidebar.items():
                if nome == "retirada":
                    btn.pack(fill="x")
                else:
                    btn.pack_forget()
            self.botoes_sidebar["monitor"].pack_forget()
        else:  # Nenhum usuário
            for btn in self.botoes_sidebar.values():
                btn.pack_forget()

    # --- ABA PRINCIPAL / PAINEL DE RETIRADA ---
    def setup_aba_principal(self, parent):
        frame = ttk.Frame(parent)
        
        # Frame para acesso por cartão/RFID
        frame_cartao = ttk.LabelFrame(frame, text="Acesso por Cartão / RFID")
        frame_cartao.pack(fill='x', padx=10, pady=10, ipady=10)

        ttk.Label(frame_cartao, text="Código do Cartão:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.entry_cartao = ttk.Entry(frame_cartao, width=20, font=FONTES["corpo"])
        self.entry_cartao.grid(row=0, column=1, padx=10, pady=10, ipady=5)
        self.entry_cartao.bind('<Return>', self.processar_cartao)

        ttk.Button(frame_cartao, text="Validar Cartão", command=self.processar_cartao).grid(row=0, column=2, padx=10, pady=10, ipady=5)

        ttk.Button(frame_cartao, text="Ler RFID", command=self.ler_rfid).grid(row=0, column=3, padx=10, pady=10, ipady=5)

        self.label_usuario_atual = ttk.Label(frame_cartao, text="Nenhum usuário identificado", foreground=CORES["alerta"])
        self.label_usuario_atual.grid(row=1, column=0, columnspan=4, pady=10)

        # Frame para busca de peça
        frame_busca = ttk.LabelFrame(frame, text="Buscar Peça para Retirada")
        frame_busca.pack(fill='x', padx=10, pady=10, ipady=10)

        ttk.Label(frame_busca, text="Nome da Peça:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.entry_busca_peca = ttk.Entry(frame_busca, width=40, font=FONTES["corpo"])
        self.entry_busca_peca.grid(row=0, column=1, padx=10, pady=10, ipady=5)
        self.entry_busca_peca.bind('<Return>', self.buscar_e_abrir_gaveta)

        ttk.Button(frame_busca, text="Buscar e Abrir Gaveta", command=self.buscar_e_abrir_gaveta).grid(row=0, column=2, padx=10, pady=10, ipady=5)

        # Status das gavetas
        frame_status = ttk.LabelFrame(frame, text="Status das Gavetas")
        frame_status.pack(fill='both', expand=True, padx=10, pady=10)

        self.labels_status_gavetas = {}
        for i in range(1, 6):
            lbl = ttk.Label(frame_status, text=f"Gaveta {i}: FECHADA", foreground='green', font=FONTES["subtitulo"])
            lbl.pack(anchor='w', pady=5, padx=10)
            self.labels_status_gavetas[i] = lbl
        
        return frame

    def ler_rfid(self):
        try:
            codigo = self.carrinho.hardware.ler_rfid()
            if codigo:
                self.entry_cartao.delete(0, tk.END)
                self.entry_cartao.insert(0, codigo)
                self.processar_cartao()
            else:
                messagebox.showinfo("RFID", "Nenhum RFID detectado (simulação ou hardware indisponível).")
        except AttributeError:
            messagebox.showinfo("RFID", "Hardware RFID não configurado. Use código manual.")

    def processar_cartao(self, event=None):
        codigo_cartao = self.entry_cartao.get().strip()
        if not codigo_cartao:
            messagebox.showwarning("Entrada Inválida", "Digite o código do cartão.")
            return

        usuario = self.carrinho.validar_cartao(codigo_cartao)
        if usuario:
            self.label_usuario_atual.config(text=f"Usuário: {usuario.nome} ({usuario.cargo}) - Perfil: {usuario.perfil}", foreground=CORES["texto_escuro"])
            self.usuario_atual = usuario
            self.configurar_acesso_por_perfil(usuario.perfil)
            self.label_usuario_header.config(text=f"Bem-vindo, {usuario.nome}!", fg=CORES["texto_claro"])
        else:
            self.label_usuario_atual.config(text="Cartão não autorizado!", foreground=CORES["alerta"])
            self.usuario_atual = None
            self.configurar_acesso_por_perfil(None)

        self.entry_cartao.delete(0, tk.END)

    # --- ABA DE USUÁRIOS (com Pop-up para Cadastro) ---
    def setup_aba_usuarios(self, parent):
        frame = ttk.Frame(parent)
        
        # Botão para abrir pop-up de cadastro (substitui o frame_add antigo)
        frame_acoes = ttk.LabelFrame(frame, text="Ações", padding=10)
        frame_acoes.pack(fill='x', padx=10, pady=5)
        ttk.Button(frame_acoes, text="Cadastrar Novo Usuário", command=self.mostrar_popup_cadastro_usuario).pack(pady=10)

        frame_lista = ttk.LabelFrame(frame, text="Usuários Cadastrados", padding=10)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Nome', 'Cargo', 'Perfil', 'Data Cadastro')
        self.tree_usuarios = ttk.Treeview(frame_lista, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=150)

        scrollbar_usuarios = ttk.Scrollbar(frame_lista, orient='vertical', command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scrollbar_usuarios.set)
        self.tree_usuarios.pack(side='left', fill='both', expand=True)
        scrollbar_usuarios.pack(side='right', fill='y')

        frame_botoes_lista = ttk.Frame(frame_lista)
        frame_botoes_lista.pack(fill='x', pady=5)

        ttk.Button(frame_botoes_lista, text="Atualizar Lista", command=self.atualizar_lista_usuarios).pack(side='left', padx=5)
        ttk.Button(frame_botoes_lista, text="Remover Selecionado", command=self.remover_usuario_selecionado).pack(side='left', padx=5)

        self.atualizar_lista_usuarios()
        return frame

  # Em ui/interface.py, SUBSTITUA este método:

    def mostrar_popup_cadastro_usuario(self):
        popup = tk.Toplevel(self.root)
        popup.title("Cadastrar Novo Usuário")
        popup.geometry("450x450")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg=CORES["fundo_secundario"])

        # Título SENAI
        tk.Label(popup, text="SENAI", font=("Segoe UI", 24, "bold"), fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(20, 0))
        tk.Label(popup, text="CADASTRAR NOVO USUÁRIO", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(0, 20))

        # Frame para o formulário
        form_frame = tk.Frame(popup, bg=CORES["fundo_secundario"])
        form_frame.pack(padx=30, pady=10)

        # Campos do formulário
        campos = ["ID do Cartão:", "Nome:", "Cargo:", "Perfil:"]
        entries = {}

        for i, campo in enumerate(campos):
            lbl = tk.Label(form_frame, text=campo, font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"])
            lbl.grid(row=i, column=0, sticky="w", pady=8, padx=5)
            
            if campo == "Perfil:":
                combo_perfil = ttk.Combobox(form_frame, values=["admin", "aluno"], width=23, state="readonly")
                combo_perfil.grid(row=i, column=1, sticky="ew", pady=8, padx=5)
                combo_perfil.set("aluno")
                entries[campo] = combo_perfil
            else:
                entry = ttk.Entry(form_frame, width=25)
                entry.grid(row=i, column=1, sticky="ew", pady=8, padx=5)
                entries[campo] = entry

        def salvar_novo_usuario():
            id_cartao = entries["ID do Cartão:"].get().strip()
            nome = entries["Nome:"].get().strip()
            cargo = entries["Cargo:"].get().strip()
            perfil = entries["Perfil:"].get().strip()

            if not all([id_cartao, nome, cargo, perfil]):
                messagebox.showerror("Erro", "Preencha todos os campos!", parent=popup)
                return

            usuario = UsuarioCartao(id=id_cartao, nome=nome, cargo=cargo, perfil=perfil, data_cadastro=datetime.datetime.now().isoformat())
            try:
                self.carrinho.db.adicionar_usuario(usuario)
                messagebox.showinfo("Sucesso", f"Usuário {nome} cadastrado!", parent=popup)
                popup.destroy()
                self.atualizar_lista_usuarios()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}", parent=popup)

        # Botões de ação estilizados
        frame_botoes = tk.Frame(popup, bg=CORES["fundo_secundario"])
        frame_botoes.pack(pady=30)

        btn_salvar = tk.Button(frame_botoes, text="Salvar Usuário", font=FONTES["botao"], bg=CORES["sucesso"],
                               fg="white", relief="flat", padx=20, pady=8, borderwidth=0, command=salvar_novo_usuario)
        btn_salvar.pack(side="left", padx=10)

        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", font=FONTES["botao"], bg=CORES["cancelar"],
                                 fg="white", relief="flat", padx=20, pady=8, borderwidth=0, command=popup.destroy)
        btn_cancelar.pack(side="left", padx=10)

    # --- ABA DE HISTÓRICO ---
    def setup_aba_historico(self, parent):
        frame = ttk.Frame(parent)
        
        frame_historico = ttk.LabelFrame(frame, text="Histórico de Eventos", padding=10)
        frame_historico.pack(fill='both', expand=True, padx=10, pady=5)

        columns_hist = ('Data/Hora', 'Gaveta', 'Usuário', 'Ação', 'Status')
        self.tree_historico = ttk.Treeview(frame_historico, columns=columns_hist, show='headings', height=15)

        for col in columns_hist:
            self.tree_historico.heading(col, text=col)
            self.tree_historico.column(col, width=150)

        scrollbar_hist = ttk.Scrollbar(frame_historico, orient='vertical', command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar_hist.set)
        self.tree_historico.pack(side='left', fill='both', expand=True)
        scrollbar_hist.pack(side='right', fill='y')

        ttk.Button(frame_historico, text="Atualizar Histórico", command=self.atualizar_historico).pack(pady=5)
        self.atualizar_historico()
        return frame

    # --- ABA DE INVENTÁRIO (com Pop-up para Cadastro de Peças e Pendências) ---
    def setup_aba_inventario(self, parent):
        frame = ttk.Frame(parent)
        
        # Botão para abrir pop-up de cadastro de peças (substitui o frame_gerenciar antigo)
        frame_acoes = ttk.LabelFrame(frame, text="Ações", padding=10)
        frame_acoes.pack(fill='x', padx=10, pady=5)
        ttk.Button(frame_acoes, text="Adicionar/Atualizar Peça", command=self.mostrar_popup_cadastro_peca).pack(pady=10)

        # Lista de peças (mantida "bonita" e inalterada)
        frame_lista_pecas = ttk.LabelFrame(frame, text="Todas as Peças", padding=10)
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

        ttk.Button(frame_lista_pecas, text="Atualizar Lista de Peças", command=self.atualizar_lista_pecas).pack(pady=5)
        
        # Pendências por usuário (integrado, só para admin)
        frame_pendencias = ttk.LabelFrame(frame, text="Pendências de Peças por Usuário", padding=10)
        frame_pendencias.pack(fill='both', expand=True, padx=10, pady=5)

        ttk.Label(frame_pendencias, text="Selecione Usuário:", font=FONTES["subtitulo"]).pack(anchor='w', padx=5, pady=5)
        self.combo_usuario_pendencias = ttk.Combobox(frame_pendencias, width=30, font=FONTES["corpo"])
        self.combo_usuario_pendencias.pack(anchor='w', padx=5, pady=5)
        self.combo_usuario_pendencias.bind('<<ComboboxSelected>>', self.atualizar_pendencias_usuario)

        ttk.Button(frame_pendencias, text="Atualizar Pendências", command=self.atualizar_pendencias_usuario).pack(pady=5)

        columns_pend = ('Peça', 'Qtd Retirada', 'Qtd Devolvida', 'Pendente', 'Data Retirada', 'Status')
        self.tree_pendencias = ttk.Treeview(frame_pendencias, columns=columns_pend, show='headings', height=8)

        for col in columns_pend:
            self.tree_pendencias.heading(col, text=col)
            self.tree_pendencias.column(col, width=120)

        scrollbar_pend = ttk.Scrollbar(frame_pendencias, orient='vertical', command=self.tree_pendencias.yview)
        self.tree_pendencias.configure(yscrollcommand=scrollbar_pend.set)
        self.tree_pendencias.pack(side='left', fill='both', expand=True, pady=5)
        scrollbar_pend.pack(side='right', fill='y')

        self.atualizar_lista_pecas()
        self.atualizar_combo_usuarios_pendencias()
        self.atualizar_pendencias_usuario()
        return frame

    # Em ui/interface.py, SUBSTITUA este método:

    def mostrar_popup_cadastro_peca(self):
        popup = tk.Toplevel(self.root)
        popup.title("Adicionar/Atualizar Peça")
        popup.geometry("450x480")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg=CORES["fundo_secundario"])

        # Título SENAI
        tk.Label(popup, text="SENAI", font=("Segoe UI", 24, "bold"), fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(20, 0))
        tk.Label(popup, text="ADICIONAR/ATUALIZAR PEÇA", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(0, 20))

        # Frame para o formulário
        form_frame = tk.Frame(popup, bg=CORES["fundo_secundario"])
        form_frame.pack(padx=30, pady=10)

        # Campos do formulário
        campos = ["Nome:", "Categoria:", "Descrição:", "Tipo:", "Gaveta ID (1-5):", "Quantidade Disponível:"]
        entries = {}

        for i, campo in enumerate(campos):
            lbl = tk.Label(form_frame, text=campo, font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"])
            lbl.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            entry = ttk.Entry(form_frame, font=FONTES["corpo"], width=30)
            entry.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            entries[campo] = entry

        # Foco inicial no campo Nome
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

        # Botões de ação estilizados
        frame_botoes = tk.Frame(popup, bg=CORES["fundo_secundario"])
        frame_botoes.pack(pady=20)

        btn_salvar = tk.Button(frame_botoes, text="Salvar Peça", font=FONTES["botao"], bg=CORES["sucesso"],
                               fg="white", relief="flat", padx=20, pady=8, borderwidth=0, command=salvar_nova_peca)
        btn_salvar.pack(side="left", padx=10)

        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", font=FONTES["botao"], bg=CORES["cancelar"],
                                 fg="white", relief="flat", padx=20, pady=8, borderwidth=0, command=popup.destroy)
        btn_cancelar.pack(side="left", padx=10)
    # --- MÉTODOS DE LÓGICA (Handlers e Funções Auxiliares) ---

    def abrir_painel_monitoramento(self):
        if not hasattr(self, 'painel_monitoramento') or not self.painel_monitoramento.root.winfo_exists():
            self.painel_monitoramento = PainelMonitoramento(self.carrinho)
        else:
            self.painel_monitoramento.root.lift()
    
    def buscar_e_abrir_gaveta(self, event=None):
        if not self.usuario_atual:
            messagebox.showerror("Acesso Negado", "Realize o login com um cartão autorizado antes de retirar uma peça.")
            return

        nome_peca = self.entry_busca_peca.get().strip()
        if not nome_peca:
            messagebox.showwarning("Entrada Inválida", "Digite o nome da peça para buscar.")
            return

        pecas = self.carrinho.db.listar_todas_pecas()
        peca_encontrada = next((p for p in pecas if nome_peca.lower() in p.nome.lower()), None)

        if not peca_encontrada:
            messagebox.showerror("Não Encontrado", f"Peça '{nome_peca}' não encontrada no inventário.")
            return

        gaveta_id = peca_encontrada.gaveta_id
        if self.carrinho.gavetas[gaveta_id].aberta:
            messagebox.showinfo("Aviso", f"A Gaveta {gaveta_id} já está aberta.")
            return
            
        sucesso = self.carrinho.abrir_gaveta(gaveta_id, self.usuario_atual.id)
        if sucesso:
            messagebox.showinfo("Sucesso", f"Gaveta {gaveta_id} aberta para a peça '{peca_encontrada.nome}'.")
            self.mostrar_pop_up_retirada(gaveta_id)
        else:
            messagebox.showerror("Erro", f"Falha ao abrir Gaveta {gaveta_id}. Verifique se não há outra gaveta aberta.")
        
        self.atualizar_status_gavetas()
        self.entry_busca_peca.delete(0, tk.END)

    def mostrar_pop_up_retirada(self, gaveta_id):
        popup = tk.Toplevel(self.root)
        popup.title(f"Registrar Retirada - Gaveta {gaveta_id}")
        popup.geometry("450x350")
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg=CORES["fundo_widget"])

        ttk.Label(popup, text=f"Peças disponíveis na Gaveta {gaveta_id}:", font=FONTES["subtitulo"]).pack(pady=(20, 10))

        pecas = self.carrinho.listar_pecas_por_gaveta(gaveta_id)
        if not pecas:
            ttk.Label(popup, text="Nenhuma peça cadastrada nesta gaveta.", font=FONTES["corpo"], foreground=CORES["alerta"]).pack(pady=10)
            ttk.Button(popup, text="Fechar", command=popup.destroy).pack(pady=10)
            return
        
        valores_pecas = [f"{p.nome} (Estoque: {p.quantidade_disponivel}) [ID: {p.id}]" for p in pecas]
        
        combo_retirada_peca = ttk.Combobox(popup, values=valores_pecas, width=40, font=FONTES["corpo"])
        combo_retirada_peca.pack(pady=5, padx=20, ipady=4)
        if valores_pecas:
            combo_retirada_peca.set(valores_pecas[0])
            
        ttk.Label(popup, text="Quantidade a Retirar:", font=FONTES["corpo"]).pack(pady=(10,5))
        entry_retirada_qtd = ttk.Entry(popup, width=10, font=FONTES["corpo"], justify="center")
        entry_retirada_qtd.pack(pady=5)
        entry_retirada_qtd.insert(0, "1")
        entry_retirada_qtd.insert(0, "1")

        def registrar_uma_retirada():
            try:
                selected = combo_retirada_peca.get()
                if not selected:
                    raise ValueError("Nenhuma peça selecionada")
                peca_id = int(selected.split("[ID:")[1].split("]")[0])
                qtd = int(entry_retirada_qtd.get())
            except (ValueError, IndexError):
                messagebox.showerror("Erro", "Seleção ou quantidade inválida!", parent=popup)
                return

            peca = self.carrinho.db.obter_peca_por_id(peca_id)
            if not peca or qtd <= 0 or peca.quantidade_disponivel < qtd:
                msg = f"Estoque insuficiente! Disponível: {peca.quantidade_disponivel if peca else 0}"
                messagebox.showerror("Erro de Estoque", msg, parent=popup)
                return

            if self.carrinho.registrar_retirada_peca(self.usuario_atual.id, peca_id, qtd):
                messagebox.showinfo("Sucesso", f"{qtd} unidades de '{peca.nome}' retiradas com sucesso!", parent=popup)
                popup.destroy()
                self.atualizar_lista_pecas()
                self.atualizar_status_gavetas()
                # Opcional: Fechar gaveta após retirada (depende da lógica do carrinho)
                # self.carrinho.fechar_gaveta(gaveta_id)
            else:
                messagebox.showerror("Erro", "Falha ao registrar retirada.", parent=popup)

        frame_botoes = ttk.Frame(popup)
        frame_botoes.pack(pady=20)
        ttk.Button(frame_botoes, text="Registrar Retirada", command=registrar_uma_retirada).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Cancelar", command=popup.destroy).pack(side="left", padx=10)

    def atualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        usuarios = self.carrinho.db.listar_usuarios()
        for usuario in usuarios:
            data_cadastro = usuario.data_cadastro or "N/A"
            try:
                data_cadastro = datetime.datetime.fromisoformat(data_cadastro).strftime("%d/%m/%Y %H:%M")
            except: 
                pass
            self.tree_usuarios.insert('', 'end', values=(usuario.id, usuario.nome, usuario.cargo, usuario.perfil, data_cadastro))

    def remover_usuario_selecionado(self):
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um usuário para remover!")
            return
        item = self.tree_usuarios.item(selection[0])
        usuario_id = item['values'][0]
        nome_usuario = item['values'][1]
        if messagebox.askyesno("Confirmar", f"Deseja realmente remover o usuário {nome_usuario}? (Isso apenas o desativará)"):
            try:
                conn = sqlite3.connect(self.carrinho.db.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE usuarios SET ativo = 0 WHERE id = ?', (usuario_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", f"Usuário {nome_usuario} removido!")
                self.atualizar_lista_usuarios()
                self.atualizar_combo_usuarios_pendencias()  # Atualiza combo de pendências
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover usuário: {e}")

    def atualizar_historico(self):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        eventos = self.carrinho.db.obter_historico(100)
        for evento in eventos:
            timestamp = evento.timestamp
            try:
                timestamp = datetime.datetime.fromisoformat(timestamp).strftime("%d/%m/%Y %H:%M:%S")
            except: 
                pass
            status = "✓ Sucesso" if evento.sucesso else "✗ Falha"
            usuario = self.carrinho.db.obter_usuario(evento.usuario_id)
            nome_usuario = usuario.nome if usuario else evento.usuario_id
            self.tree_historico.insert('', 'end', values=(timestamp, f"Gaveta {evento.gaveta_id}", nome_usuario, evento.acao.capitalize(), status))

    def atualizar_lista_pecas(self):
        if hasattr(self, 'tree_pecas'):
            for item in self.tree_pecas.get_children():
                self.tree_pecas.delete(item)
            pecas = self.carrinho.listar_todas_pecas()
            for peca in pecas:
                desc_short = peca.descricao[:30] + '...' if len(peca.descricao) > 30 else peca.descricao
                self.tree_pecas.insert('', 'end', values=(
                    peca.id, peca.nome, peca.categoria, desc_short, peca.tipo, peca.gaveta_id, peca.quantidade_disponivel
                ))

    def atualizar_combo_usuarios_pendencias(self):
        usuarios = self.carrinho.db.listar_usuarios()
        nomes_usuarios = [u.nome for u in usuarios if u.ativo]  # Apenas usuários ativos
        self.combo_usuario_pendencias['values'] = nomes_usuarios
        if nomes_usuarios:
            self.combo_usuario_pendencias.set(nomes_usuarios[0])

    def atualizar_pendencias_usuario(self, event=None):
        nome_usuario = self.combo_usuario_pendencias.get()
        if not nome_usuario:
            return
        usuarios = self.carrinho.db.listar_usuarios()
        usuario = next((u for u in usuarios if u.nome == nome_usuario and u.ativo), None)
        if not usuario:
            messagebox.showwarning("Aviso", "Usuário não encontrado ou inativo.")
            return

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

    def atualizar_status_gavetas(self):
        for gaveta_id, gaveta in self.carrinho.gavetas.items():
            label = self.labels_status_gavetas.get(gaveta_id)
            if label:
                if gaveta.aberta:
                    tempo_aberta = gaveta.tempo_aberta()
                    texto_tempo = f" (aberta há {tempo_aberta//60}m {tempo_aberta%60}s)"
                    label.config(text=f"Gaveta {gaveta_id}: ABERTA{texto_tempo}", foreground=CORES["alerta"])
                else:
                    label.config(text=f"Gaveta {gaveta_id}: FECHADA", foreground='green')

    def atualizar_status_periodico(self):
        self.atualizar_status_gavetas()
        self.root.after(2000, self.atualizar_status_periodico)  # Atualiza a cada 2 segundos

    def _on_close(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema? Todas as gavetas abertas serão fechadas."):
            # Fecha todas as gavetas abertas
            for gaveta_id in self.carrinho.gavetas:
                if self.carrinho.gavetas[gaveta_id].aberta:
                    self.carrinho.fechar_gaveta(gaveta_id)
            self.carrinho.sistema_ativo = False
            if hasattr(self, 'painel_monitoramento') and self.painel_monitoramento.root.winfo_exists():
                self.painel_monitoramento.root.destroy()
            self.root.destroy()
            logging.info("Sistema encerrado pelo usuário.")

    def executar(self):
        self.root.mainloop()


# Exemplo de uso (para testar standalone, se necessário)
if __name__ == "__main__":
    interface = InterfaceGraficaCarrinho()
    interface.executar()