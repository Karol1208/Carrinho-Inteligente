import customtkinter as ctk
from tkinter import messagebox
import logging
from PIL import Image
import os

from core.cart import CarrinhoInteligenteAvancado
from ui.painelMonitoramento import PainelMonitoramento
from ui.theme import CORES, FONTES
from ui.cadastro import TelaCadastroRFID
from ui.components.glass_card import GlassCard
from ui.components.primary_button import PrimaryButton

from ui.abas.aba_principal import AbaPrincipal
from ui.abas.aba_usuarios import AbaUsuarios
from ui.abas.aba_inventario import AbaInventario
from ui.abas.aba_historico import AbaHistorico
from ui.components.status_bar import StatusBar


class InterfaceGraficaCarrinho:
    """Classe principal que gerencia a janela, a navegação e a comunicação entre as abas."""
    
    def __init__(self, carrinho: CarrinhoInteligenteAvancado = None, usuario_inicial=None):
        self.carrinho = carrinho if carrinho else CarrinhoInteligenteAvancado()
        
        # Inicialização do CustomTkinter
        self.root = ctk.CTk()
        self.root.title("CRDF - Painel de Controle Premium")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 750)
        self.root.configure(fg_color=CORES["fundo_principal"])
        
        ctk.set_appearance_mode("dark")
        
        self.usuario_atual = usuario_inicial
        self.frames_conteudo = {}
        self.botoes_sidebar = {}
        
        self.aba_principal = None
        self.aba_usuarios = None
        self.aba_inventario = None
        self.aba_historico = None
        self.after_tasks = []
        self.icones = {}
        self.carregar_icones()

        self.setup_interface_principal()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.atualizar_status_periodico()

        # Atualiza status bar com estado real do hardware
        hw_online = hasattr(self.carrinho, 'hardware') and getattr(self.carrinho.hardware, 'is_running', False)
        self.status_bar.set_hw_status(hw_online)

        # Configuração de acesso
        if self.usuario_atual:
            self.configurar_acesso_por_perfil(self.usuario_atual.perfil)
        else:
            self.configurar_acesso_por_perfil(None)

        # Timer de Inatividade
        self.inactivity_timer_id = None
        self.INACTIVITY_TIMEOUT = 300000  # 5 minutos (60000 * 5)
        
        self.root.bind_all("<Button-1>", self._on_user_activity)
        self.root.bind_all("<Key>", self._on_user_activity)
        self._resetar_timer_inatividade()

    def safe_after(self, delay, callback):
        """Agenda uma tarefa após um delay de forma segura."""
        if self.root.winfo_exists():
            task_id = self.root.after(delay, callback)
            self.after_tasks.append(task_id)
            return task_id
        return None

    def limpar_tasks(self):
        """Cancela todas as tarefas agendadas pendentes."""
        for task in self.after_tasks:
            try:
                self.root.after_cancel(task)
            except:
                pass
        self.after_tasks.clear()

    def setup_interface_principal(self):
        # 1. Sidebar (Esquerda)
        self.sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0, fg_color=CORES["fundo_secundario"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo no Topo da Sidebar
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=40, padx=20, fill="x")
        
        try:
            logo_data = Image.open("assets/logo_senai.png")
            logo_img = ctk.CTkImage(light_image=logo_data, dark_image=logo_data, size=(180, 60))
            ctk.CTkLabel(logo_frame, image=logo_img, text="").pack()
        except:
            ctk.CTkLabel(logo_frame, text="CRDF PREMIUM", font=FONTES["titulo"], text_color=CORES["texto_claro"]).pack()

        # Botões de Navegação
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.pack(fill="both", expand=True, padx=10)

        # Layout Principal (Direita)
        self.main_layout = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_layout.pack(side="right", fill="both", expand=True)

        # 2. Header (Topo do Layout Principal)
        self.header = ctk.CTkFrame(self.main_layout, height=80, corner_radius=0, fg_color="transparent")
        self.header.pack(side="top", fill="x", padx=30, pady=(20, 0))
        
        self.lbl_page_title = ctk.CTkLabel(
            self.header, 
            text="Painel de Retirada", 
            font=FONTES["titulo"],
            text_color=CORES["texto_claro"]
        )
        self.lbl_page_title.pack(side="left")

        # Info Usuário e Botão Sair no Header
        user_info_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        user_info_frame.pack(side="right")

        self.label_usuario_header = ctk.CTkLabel(
            user_info_frame, 
            text="Nenhum usuário logado", 
            font=FONTES["corpo"],
            text_color=CORES["texto_muted"]
        )
        self.label_usuario_header.pack(side="left", padx=20)

        self.btn_sair = ctk.CTkButton(
            user_info_frame,
            text="SAIR",
            width=100,
            height=35,
            fg_color=CORES["cancelar"],
            hover_color="#c0392b",
            font=FONTES["botao"],
            command=self._logout_manual
        )
        self.btn_sair.pack(side="right")

        # 3. Área de Conteúdo
        self.content_container = GlassCard(self.main_layout)
        self.content_container.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        
        # 4. Barra de Status (Bottom)
        self.status_bar = StatusBar(self.main_layout)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Inicialização das Abas
        self.aba_principal = AbaPrincipal(self.content_container, self.carrinho, self)
        self.aba_usuarios = AbaUsuarios(self.content_container, self.carrinho, self)
        self.aba_historico = AbaHistorico(self.content_container, self.carrinho, self)
        self.aba_inventario = AbaInventario(self.content_container, self.carrinho, self)
        
        self.frames_conteudo = {
            "retirada": self.aba_principal,
            "usuarios": self.aba_usuarios,
            "historico": self.aba_historico,
            "inventario": self.aba_inventario
        }

        # Criação dos Botões da Sidebar
        self.criar_botoes_nav()
        
        self.mostrar_frame("retirada")

    def abrir_tela_cadastro_rfid(self):
        tela_rfid = TelaCadastroRFID(
            self.carrinho, 
            root_principal=self.root, 
            callback_atualizar_usuarios=self.aba_usuarios.atualizar_lista_usuarios
        )
        tela_rfid.executar()

    def carregar_icones(self):
        icon_map = {
            "retirada": "icon_home.png",
            "inventario": "icon_inventory.png",
            "usuarios": "icon_users.png",
            "historico": "icon_history.png",
            "monitor": "icon_alert.png"
        }
        for name, path in icon_map.items():
            try:
                full_path = os.path.join("assets", path)
                image = Image.open(full_path)
                self.icones[name] = ctk.CTkImage(image, image, size=(32, 32
                ))
            except Exception as e:
                logging.warning(f"Erro ao carregar ícone {path}: {e}")
                self.icones[name] = None

    def criar_botoes_nav(self):
        botoes_nav = {
            "retirada": "Dashboard / Retirada",
            "inventario": "Inventário",
            "usuarios": "Gerenciar Usuários",
            "historico": "Histórico Geral"
        }

        for id_nome, texto in botoes_nav.items():
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"  {texto}",
                image=self.icones.get(id_nome),
                font=FONTES["botao"],
                anchor="w",
                height=55,
                fg_color="transparent",
                text_color=CORES["texto_claro"],
                hover_color=CORES["glass_borda"],
                command=lambda f=id_nome: self.mostrar_frame(f)
            )
            # CORREÇÃO: Empacota o botão imediatamente no nav_frame
            # configurar_acesso_por_perfil vai esconder/mostrar conforme o perfil
            btn.pack(fill="x", pady=2, padx=5)
            self.botoes_sidebar[id_nome] = btn

        # Botão Especial de Monitoramento (parte inferior da sidebar)
        self.btn_monitor = ctk.CTkButton(
            self.sidebar,
            text="  Monitor de Pendências",
            image=self.icones.get("monitor"),
            font=FONTES["botao"],
            anchor="w",
            height=55,
            fg_color="transparent",
            text_color=CORES["alerta"],
            hover_color=CORES["glass_borda"],
            command=self.abrir_painel_monitoramento
        )
        self.botoes_sidebar["monitor"] = self.btn_monitor
        self.btn_monitor.pack(side="bottom", fill="x", padx=10, pady=20)

    def mostrar_frame(self, nome_frame):
        # Atualiza título da página
        titulos = {
            "retirada": "Painel de Retirada",
            "usuarios": "Gerenciamento de Usuários",
            "historico": "Histórico de Transações",
            "inventario": "Inventário de Ferramentas"
        }
        self.lbl_page_title.configure(text=titulos.get(nome_frame, "Dashboard"))

        # Alterna visibilidade
        for frame in self.frames_conteudo.values():
            frame.grid_remove()
        
        frame_ativo = self.frames_conteudo.get(nome_frame)
        if frame_ativo:
            frame_ativo.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Realça botão ativo na sidebar
        for nome, btn in self.botoes_sidebar.items():
            if nome != 'monitor':
                if nome == nome_frame:
                    btn.configure(fg_color=CORES["destaque"], text_color="white")
                else:
                    btn.configure(fg_color="transparent", text_color=CORES["texto_claro"])

    def configurar_acesso_por_perfil(self, perfil):
        # Esconde todos os botões de navegação primeiro
        for btn in self.botoes_sidebar.values():
            if btn != self.btn_monitor:
                btn.pack_forget()

        # Atualiza cabeçalho
        if self.usuario_atual:
            self.label_usuario_header.configure(text=f"Autenticado: {self.usuario_atual.nome} ({perfil.upper()})")
        else:
            self.label_usuario_header.configure(text="Sessão não identificada")

        # Define visibilidade por perfil
        if perfil == "admin":
            self.botoes_sidebar["retirada"].pack(fill="x", padx=5, pady=2)
            self.botoes_sidebar["inventario"].pack(fill="x", padx=5, pady=2)
            self.botoes_sidebar["usuarios"].pack(fill="x", padx=5, pady=2)
            self.botoes_sidebar["historico"].pack(fill="x", padx=5, pady=2)
        elif perfil == "aluno":
            self.botoes_sidebar["retirada"].pack(fill="x", padx=5, pady=2)
        else:
            self.botoes_sidebar["retirada"].pack(fill="x", padx=5, pady=2)

    def atualizar_status_periodico(self):
        if not self.root.winfo_exists():
            return
        if self.aba_principal:
            self.aba_principal.atualizar_status_gavetas()
        # Atualiza status bar com o estado atual do hardware
        hw_online = hasattr(self.carrinho, 'hardware') and getattr(self.carrinho.hardware, 'is_running', False)
        if hasattr(self, 'status_bar'):
            self.status_bar.set_hw_status(hw_online)
        self.safe_after(1000, self.atualizar_status_periodico)

    def abrir_painel_monitoramento(self):
        if not hasattr(self, 'painel_monitoramento') or not self.painel_monitoramento.root.winfo_exists():
            self.painel_monitoramento = PainelMonitoramento(self.carrinho)
        else:
            self.painel_monitoramento.root.lift()
            self.painel_monitoramento.root.focus_force()

    def _on_user_activity(self, event=None):
        self._resetar_timer_inatividade()

    def _resetar_timer_inatividade(self):
        if self.inactivity_timer_id:
            try: self.root.after_cancel(self.inactivity_timer_id)
            except: pass
        self.inactivity_timer_id = self.safe_after(self.INACTIVITY_TIMEOUT, self._logout_por_inatividade)
        if self.inactivity_timer_id in self.after_tasks:
            self.after_tasks.remove(self.inactivity_timer_id) # Timers de inatividade são gerenciados manualmente

    def _logout_por_inatividade(self):
        logging.info("Sessão expirada por inatividade.")
        messagebox.showwarning("Sessão Expirada", "Você foi desconectado automaticamente por inatividade.", parent=self.root)
        self._on_close(force_close=True)

    def _logout_manual(self):
        self._on_close(force_close=True)

    def _on_close(self, force_close=False):
        confirmar = force_close or messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?")
        if confirmar:
            self.limpar_tasks()
            if self.inactivity_timer_id:
                try: self.root.after_cancel(self.inactivity_timer_id)
                except: pass
            
            if self.carrinho and hasattr(self.carrinho.hardware, 'close'):
                self.carrinho.hardware.close()
            
            self.root.destroy()

    def executar(self):
        self.root.mainloop()
