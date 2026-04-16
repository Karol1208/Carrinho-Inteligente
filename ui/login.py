import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import logging
from ui.theme import CORES, FONTES
from ui.components.glass_card import GlassCard
from ui.components.primary_button import PrimaryButton
from ui.components.modern_input import ModernInput

class TelaLogin:
    def __init__(self, carrinho):
        self.carrinho = carrinho
        self.usuario = None
        self.perfil = None
        self.modo_rfid = True
        self.after_tasks = []
        self.pulse_val = 0
        self.pulse_dir = 1

        self.root = ctk.CTk()
        self.root.title("Login - CRDF Premium")
        self.root.geometry("600x750")
        self.root.configure(fg_color=CORES["fundo_principal"])
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")
        
        try:
            import os
            icon_png_path = os.path.join("assets", "crdf_icon.png")
            icon_ico_path = os.path.join("assets", "crdf_icon.ico")
            if os.path.exists(icon_png_path):
                img = Image.open(icon_png_path)
                img.save(icon_ico_path, format="ICO", sizes=[(32, 32), (64, 64)])
                self.root.iconbitmap(icon_ico_path)
        except Exception as e:
            logging.warning(f"Erro ao setar favicon log: {e}")
        
        self.centralizar_janela()
        self.setup_interface()

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

    def centralizar_janela(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
       
    def setup_interface(self):
        # Container Principal
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=40, pady=40)

        # Header com Logos
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))

        try:
            logo_senai_data = Image.open("assets/logo_senai.png")
            logo_senai = ctk.CTkImage(light_image=logo_senai_data, dark_image=logo_senai_data, size=(150, 50))
            ctk.CTkLabel(header_frame, image=logo_senai, text="").pack(side="left")
        except:
            ctk.CTkLabel(header_frame, text="SENAI", font=("Segoe UI", 24, "bold"), text_color=CORES["texto_claro"]).pack(side="left")

        try:
            icon_data = Image.open("assets/crdf_icon.png")
            icon = ctk.CTkImage(light_image=icon_data, dark_image=icon_data, size=(60, 60))
            ctk.CTkLabel(header_frame, image=icon, text="").pack(side="right")
        except:
            pass

        # Título e Subtítulo
        title_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        title_frame.pack(pady=(0, 40))

        ctk.CTkLabel(
            title_frame, 
            text="CRDF", 
            font=FONTES["titulo"],
            text_color=CORES["texto_claro"]
        ).pack()
        
        ctk.CTkLabel(
            title_frame, 
            text="Sistema Inteligente de Ferramentas", 
            font=FONTES["subtitulo"], 
            text_color=CORES["texto_muted"]
        ).pack()

        # Card de Login (Glassmorphism)
        self.login_card = GlassCard(self.main_container)
        self.login_card.pack(fill="x", pady=10, ipady=20)

        # Conteúdo do Card (Alternável)
        self.content_frame = ctk.CTkFrame(self.login_card, fg_color="transparent")
        self.content_frame.pack(padx=30, pady=30, fill="both")

        # Ícone de Status / RFID
        self.status_icon_label = ctk.CTkLabel(self.content_frame, text="", height=100)
        self.status_icon_label.pack(pady=(0, 10))

        self.status_text = ctk.CTkLabel(
            self.content_frame, 
            text="Aguardando Aproximação...", 
            font=FONTES["subtitulo"],
            text_color=CORES["alerta"]
        )
        self.status_text.pack(pady=10)

        # Carrega o ícone agora que os textos estão prontos (evita AttributeError)
        self.load_rfid_icon()

        # Campo de Entrada Manual (Escondido initially)
        self.manual_entry = ModernInput(self.content_frame, placeholder_text="Digite o código do cartão")
        self.manual_entry.bind("<Return>", self.validar_login_manual)

        # Botões de Ação
        self.btn_entrar = PrimaryButton(self.content_frame, "ENTRAR NO SISTEMA", command=self.validar_login_manual)
        
        self.btn_alternar = ctk.CTkButton(
            self.main_container,
            text="Utilizar Entrada Manual",
            fg_color="transparent",
            text_color=CORES["destaque"],
            hover_color=CORES["fundo_secundario"],
            font=FONTES["corpo"],
            command=self.alternar_modo_entrada
        )
        self.btn_alternar.pack(pady=20)

        # Inicializa estado
        self.atualizar_modo_entrada()

    def load_rfid_icon(self):
        try:
            icon_data = Image.open("assets/rfid_icon.png")
            self.rfid_image = ctk.CTkImage(light_image=icon_data, dark_image=icon_data, size=(120, 120))
            self.status_icon_label.configure(image=self.rfid_image)
            self.iniciar_animacao_pulso()
        except Exception as e:
            logging.error(f"Erro ao carregar ícone RFID: {e}")
            self.status_icon_label.configure(text="📡", font=("Segoe UI Variable", 48))

    def iniciar_animacao_pulso(self):
        if not self.root.winfo_exists() or not self.modo_rfid:
            return
        
        # Efeito de pulso simples alterando o tamanho levemente (simulado)
        # Ou mudando a cor do texto/alpha se suportado, mas CTkImage é fixo.
        # Vamos alternar entre duas cores de texto se for fallback ou apenas manter o timer
        self.pulse_val += 5 * self.pulse_dir
        if self.pulse_val >= 100 or self.pulse_val <= 0:
            self.pulse_dir *= -1
            
        color_val = int(150 + (self.pulse_val * 1.05)) # Oscila entre 150 e 255
        hex_color = f"#{color_val:02x}{color_val:02x}00" # Amarelo pulsante
        
        self.status_text.configure(text_color=hex_color)
        self.safe_after(50, self.iniciar_animacao_pulso)

    def alternar_modo_entrada(self):
        self.modo_rfid = not self.modo_rfid
        self.atualizar_modo_entrada()

    def atualizar_modo_entrada(self):
        if self.modo_rfid:
            self.manual_entry.pack_forget()
            self.btn_entrar.pack_forget()
            self.status_icon_label.pack(pady=(0, 10))
            self.status_text.configure(text="Aproxime seu Token RFID", text_color=CORES["alerta"])
            self.btn_alternar.configure(text="Utilizar Entrada Manual")
        else:
            self.status_icon_label.pack_forget()
            self.status_text.configure(text="Insira suas Credenciais", text_color=CORES["texto_claro"])
            self.manual_entry.pack(pady=20, fill="x")
            self.btn_entrar.pack(pady=10, fill="x")
            self.btn_alternar.configure(text="Utilizar Leitor RFID")
            self.manual_entry.focus()

    def validar_login_manual(self, event=None):
        codigo = self.manual_entry.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Por favor, digite o código do cartão.")
            return
        
        self.status_text.configure(text="Validando Acesso...", text_color=CORES["destaque"])
        self.root.update()
        self.processar_validacao(codigo)

    def processar_validacao(self, codigo):
        usuario = self.carrinho.validar_cartao(codigo)
        if usuario:
            self.status_text.configure(text="Acesso Liberado! Bem-vindo.", text_color=CORES["sucesso"])
            self.root.update()
            
            self.usuario = usuario
            self.perfil = usuario.perfil
            
            self.limpar_tasks()
            
            # Pequeno delay para o usuário ver o sucesso
            self.safe_after(800, self.safe_destroy)
        else:
            if not self.modo_rfid:
                messagebox.showerror("Erro de Acesso", "Cartão não autorizado ou inválido.")
                self.manual_entry.delete(0, 'end')
                self.status_text.configure(text="Insira suas Credenciais", text_color=CORES["texto_claro"])
            else:
                # Feedback visual de erro rápido no modo RFID
                self.status_text.configure(text="Cartão recusado. Tente novamente.", text_color=CORES["cancelar"])
                self.safe_after(2000, lambda: self.status_text.configure(text="Aproxime seu Token RFID", text_color=CORES["alerta"]) if self.root.winfo_exists() else None)

    def safe_destroy(self):
        self.limpar_tasks()
        # Remove o callback antes de destruir a janela
        try:
            self.carrinho.remover_callback_rfid(self.on_rfid_read)
        except:
            pass
        self.root.destroy()

    def on_rfid_read(self, codigo):
        """Trata o evento de leitura de RFID disparado pelo backend."""
        if not self.root.winfo_exists() or not self.modo_rfid:
            return
        
        # Como o callback vem de uma thread, precisamos agendar pro loop principal do Tkinter
        self.root.after(0, lambda: self.processar_validacao(codigo))

    def executar(self):
        # Inscreve-se no evento de leitura no backend
        self.carrinho.registrar_callback_rfid(self.on_rfid_read)
        self.root.mainloop()
        return self.usuario, self.perfil
