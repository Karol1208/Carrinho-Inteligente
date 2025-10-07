import tkinter as tk
from tkinter import ttk, messagebox
import logging
from PIL import Image, ImageTk

from core.cart import CarrinhoInteligenteAvancado
from ui.painelMonitoramento import PainelMonitoramento
from ui.theme import CORES, FONTES
from ui.cadastro import TelaCadastroRFID

from ui.abas.aba_principal import AbaPrincipal
from ui.abas.aba_usuarios import AbaUsuarios
from ui.abas.aba_inventario import AbaInventario
from ui.abas.aba_historico import AbaHistorico


class InterfaceGraficaCarrinho:
    """Classe principal que gerencia a janela, a navegação e a comunicação entre as abas."""
    # Versão NOVA e CORRIGIDA
    def __init__(self, carrinho: CarrinhoInteligenteAvancado = None, usuario_inicial=None):
        self.carrinho = carrinho if carrinho else CarrinhoInteligenteAvancado()
        self.root = tk.Tk()
        self.root.title("CRDF - Controle de Retirada e Devolução de Ferramentas")
        self.root.geometry("1280x720")
        self.root.minsize(1100, 700)
        self.root.configure(bg=CORES["fundo_widget"])

        self.usuario_atual = usuario_inicial
        self.frames_conteudo = {}
        self.botoes_sidebar = {}
        self.label_usuario_header = None
        
        self.aba_principal = None
        self.aba_usuarios = None
        self.aba_inventario = None
        self.aba_historico = None

        self.setup_estilos_ttk()
        self.setup_interface_principal()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.atualizar_status_periodico()

        # Inicia a configuração de acesso com base no usuário que fez login
        if self.usuario_atual:
            self.configurar_acesso_por_perfil(self.usuario_atual.perfil)
        else:
            # Se não houver usuário, configura um acesso padrão/limitado
            self.configurar_acesso_por_perfil(None)

    def abrir_tela_cadastro_rfid(self):
        tela_rfid = TelaCadastroRFID(self.carrinho, root_principal=self.root, callback_atualizar_usuarios=self.aba_usuarios.atualizar_lista_usuarios)
        tela_rfid.executar()
    
    def setup_estilos_ttk(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=CORES["fundo_widget"], foreground=CORES["texto_escuro"], rowheight=28, fieldbackground=CORES["fundo_widget"], font=FONTES["corpo"])
        style.map('Treeview', background=[('selected', CORES["destaque"])])
        style.configure("Treeview.Heading", background=CORES["fundo_secundario"], foreground=CORES["texto_claro"], font=FONTES["botao"], padding=(10, 10))
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

        self.aba_principal = AbaPrincipal(self.frame_conteudo_principal, self.carrinho, self)
        self.aba_usuarios = AbaUsuarios(self.frame_conteudo_principal, self.carrinho, self)
        self.aba_historico = AbaHistorico(self.frame_conteudo_principal, self.carrinho, self)
        self.aba_inventario = AbaInventario(self.frame_conteudo_principal, self.carrinho, self)
        
        self.frames_conteudo = {
            "retirada": self.aba_principal,
            "usuarios": self.aba_usuarios,
            "historico": self.aba_historico,
            "inventario": self.aba_inventario
        }
        
        self.mostrar_frame("retirada")

    def criar_cabecalho(self):
        header = tk.Frame(self.root, bg=CORES["fundo_secundario"], height=60)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.pack_propagate(False)

        try:
            logo_img = ImageTk.PhotoImage(Image.open("logo_senai.png").resize((120, 40), Image.LANCZOS))
            lbl_logo = tk.Label(header, image=logo_img, bg=CORES["fundo_secundario"])
            lbl_logo.image = logo_img 
            lbl_logo.pack(side="left", padx=20)
        except Exception as e:
            tk.Label(header, text="SENAI", font=FONTES["titulo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(side="left", padx=20)
            logging.warning(f"Não foi possível carregar 'logo_senai.png': {e}")

        self.label_usuario_header = tk.Label(header, text="", font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"])
        self.label_usuario_header.pack(side="right", padx=20)

    def criar_sidebar(self):
        sidebar = tk.Frame(self.root, bg=CORES["fundo_secundario"], width=250)
        sidebar.grid(row=1, column=0, sticky="nsw")
        sidebar.pack_propagate(False)
        
        botoes_nav = {
            "retirada": "Painel de Retirada",
            "inventario": "Inventário",
            "usuarios": "Gerenciar Usuários",
            "historico": "Histórico"
        }

        for nome, texto in botoes_nav.items():
            btn = tk.Button(sidebar, text=texto, font=FONTES["botao"], bg=CORES["fundo_secundario"], fg=CORES["texto_claro"], relief="flat", anchor="w", padx=20, pady=15, activebackground=CORES["destaque"], activeforeground=CORES["texto_claro"], command=lambda f=nome: self.mostrar_frame(f))
            self.botoes_sidebar[nome] = btn
            
        btn_monitor = tk.Button(sidebar, text="Monitor de Peças Pendentes", font=FONTES["botao"], bg=CORES["fundo_secundario"], fg=CORES["alerta"], relief="flat", anchor="w", padx=20, pady=15, activebackground=CORES["destaque"], activeforeground=CORES["texto_claro"], command=self.abrir_painel_monitoramento)
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

    # Versão NOVA e CORRIGIDA
    def configurar_acesso_por_perfil(self, perfil):
        # Esconde todos os botões da sidebar para começar do zero
        for btn in self.botoes_sidebar.values():
            btn.pack_forget()

        # Atualiza o cabeçalho com as informações do usuário
        if self.usuario_atual:
            self.label_usuario_header.config(text=f"Bem-vindo, {self.usuario_atual.nome} ({perfil})", fg=CORES["texto_claro"])
        else:
            self.label_usuario_header.config(text="Nenhum usuário logado", fg=CORES["texto_claro"])
        
        # Visibilidade do botão "Abrir Todas as Gavetas" (que está na AbaPrincipal)
        if hasattr(self.aba_principal, 'botao_abrir_todas'):
            if perfil == "admin":
                self.aba_principal.botao_abrir_todas.pack(side="left", padx=10, pady=5)
            else:
                self.aba_principal.botao_abrir_todas.pack_forget()
        
        # Exibe os botões da sidebar de acordo com o perfil
        if perfil == "admin":
            self.botoes_sidebar["retirada"].pack(fill="x")
            self.botoes_sidebar["inventario"].pack(fill="x")
            self.botoes_sidebar["usuarios"].pack(fill="x")
            self.botoes_sidebar["historico"].pack(fill="x")
            self.botoes_sidebar["monitor"].pack(fill="x", side="bottom", pady=(0, 20))
        elif perfil == "aluno":
            self.botoes_sidebar["retirada"].pack(fill="x")
            self.botoes_sidebar["historico"].pack(fill="x")
            self.botoes_sidebar["monitor"].pack(fill="x", side="bottom", pady=(0, 20))
        else: # Se não houver usuário logado
            self.botoes_sidebar["retirada"].pack(fill="x")

    def atualizar_status_periodico(self):
        if self.aba_principal:
            self.aba_principal.atualizar_status_gavetas()
        self.root.after(2000, self.atualizar_status_periodico)

    def abrir_painel_monitoramento(self):
        if not hasattr(self, 'painel_monitoramento') or not self.painel_monitoramento.root.winfo_exists():
            self.painel_monitoramento = PainelMonitoramento(self.carrinho)
        else:
            self.painel_monitoramento.root.lift()
            self.painel_monitoramento.root.focus_force()

    # ADICIONE a linha `self.carrinho.hardware.close()`
    def _on_close(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            logging.info("Sistema encerrado pelo usuário.")
            
            # Garante que a conexão com o hardware seja fechada
            if self.carrinho and hasattr(self.carrinho.hardware, 'close'):
                self.carrinho.hardware.close()
                
            # O resto do seu código de fechamento
            if hasattr(self, 'painel_monitoramento') and self.painel_monitoramento.root.winfo_exists():
                self.painel_monitoramento.root.destroy()
            self.root.destroy()

    def executar(self):
        self.root.mainloop()