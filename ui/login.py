# Em ui/login.py (VERSÃO COM ÍCONE PRÓXIMO E MAIOR)

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from ui.theme import CORES, FONTES

class TelaLogin:
    def __init__(self, carrinho):
        self.carrinho = carrinho
        self.usuario = None
        self.perfil = None
        self.modo_rfid = True

        self.root = tk.Tk()
        self.root.title("Login - CRDF")
        self.root.geometry("600x650") 
        self.root.configure(bg=CORES["fundo_principal"])
        self.root.resizable(False, False)
        self.centralizar_janela()
        self.setup_interface()
        
        # self.verificar_leitor_rfid_periodicamente()

    def centralizar_janela(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_interface(self):
        main_frame = tk.Frame(self.root, bg=CORES["fundo_principal"])
        main_frame.pack(expand=True, fill="both")

        try:
            self.logo_senai_img = ImageTk.PhotoImage(Image.open("logo_senai.png").resize((150, 50), Image.LANCZOS))
            tk.Label(main_frame, image=self.logo_senai_img, bg=CORES["fundo_principal"]).pack(pady=(20, 10))
        except:
            tk.Label(main_frame, text="SENAI", font=("Segoe UI", 20, "bold"), fg="white", bg=CORES["fundo_principal"]).pack(pady=(20, 10))
        
        frame_titulo_principal = tk.Frame(main_frame, bg=CORES["fundo_principal"])
        frame_titulo_principal.pack(pady=20, padx=30, fill="x")

        # --- AJUSTES DE TAMANHO E ESPAÇAMENTO AQUI ---
        try:
            # 1. IMAGEM MAIOR AINDA (160x160 pixels)
            self.crdf_icon_img = ImageTk.PhotoImage(Image.open("crdf_icon.png").resize((160, 160), Image.LANCZOS))
            # 2. ESPAÇAMENTO HORIZONTAL MENOR (padx=5)
            tk.Label(frame_titulo_principal, image=self.crdf_icon_img, bg=CORES["fundo_principal"]).pack(side="left", padx=5)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar 'crdf_icon.png': {e}")
        
        frame_textos = tk.Frame(frame_titulo_principal, bg=CORES["fundo_principal"])
        frame_textos.pack(side="left", expand=True, fill="x", padx=10) # Adicionei um padx aqui para não colar no ícone
        
        tk.Label(frame_textos, text="CRDF", font=("Segoe UI", 48, "bold"), fg="white", bg=CORES["fundo_principal"]).pack(anchor="w")
        tk.Label(frame_textos, text="Controle de Retirada e", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(anchor="w")
        tk.Label(frame_textos, text="Devolução de Ferramentas", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(anchor="w")
        # --- FIM DOS AJUSTES ---

        self.frame_entrada_alternavel = tk.Frame(main_frame, bg=CORES["fundo_principal"])
        self.frame_entrada_alternavel.pack(pady=20, fill="x", expand=True)
        
        self.frame_rfid_prompt = tk.Frame(self.frame_entrada_alternavel, bg=CORES["fundo_principal"])
        try:
            self.rfid_icon_img = ImageTk.PhotoImage(Image.open("rfid_icon.png").resize((100, 100), Image.LANCZOS))
            tk.Label(self.frame_rfid_prompt, image=self.rfid_icon_img, bg=CORES["fundo_principal"]).pack(pady=5)
        except: pass
        tk.Label(self.frame_rfid_prompt, text="Aproxime seu Token", font=("Segoe UI", 18, "bold"), fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(pady=10)

        self.frame_texto_prompt = tk.Frame(self.frame_entrada_alternavel, bg=CORES["fundo_principal"])
        tk.Label(self.frame_texto_prompt, text="Digite o código do seu cartão", font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(pady=5)
        self.entry_codigo = tk.Entry(self.frame_texto_prompt, font=FONTES["botao"], justify="center", width=25,
                                     bg=CORES["fundo_tabela"], fg=CORES["texto_escuro"], relief="flat")
        self.entry_codigo.pack(pady=10, ipady=8)
        self.entry_codigo.bind("<Return>", self.validar_login_manual)
        
        self.btn_alternar = tk.Button(main_frame, text="", font=FONTES["corpo"], command=self.alternar_modo_entrada, relief="flat", 
                                      bg=CORES["fundo_principal"], fg=CORES["destaque"], 
                                      activebackground=CORES["fundo_principal"], activeforeground="white", borderwidth=0)
        self.btn_alternar.pack()
        
        self.btn_login = tk.Button(main_frame, text="ENTRAR", font=FONTES["botao"], command=self.validar_login_manual, 
                               bg=CORES["sucesso"], fg="white", relief="flat", padx=40, pady=10, borderwidth=0)
        
        self.atualizar_modo_entrada()
        self.entry_codigo.focus()

    def alternar_modo_entrada(self):
        self.modo_rfid = not self.modo_rfid
        self.atualizar_modo_entrada()

    def atualizar_modo_entrada(self):
        if self.modo_rfid:
            self.frame_texto_prompt.pack_forget()
            self.frame_rfid_prompt.pack(pady=10)
            self.btn_alternar.config(text="Ou, clique para Digitar o Código")
            self.btn_login.pack_forget()
        else:
            self.frame_rfid_prompt.pack_forget()
            self.frame_texto_prompt.pack(pady=10)
            self.btn_alternar.config(text="Ou, clique para Usar o Leitor RFID")
            self.btn_login.pack(pady=20)
            self.entry_codigo.focus()

    def validar_login_manual(self, event=None):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Por favor, digite o código do cartão.")
            return
        self.processar_validacao(codigo)

    def processar_validacao(self, codigo):
        usuario = self.carrinho.validar_cartao(codigo)
        if usuario:
            self.usuario = usuario
            self.perfil = usuario.perfil
            if hasattr(self, 'after_id'): self.root.after_cancel(self.after_id)
            self.root.destroy()
        elif not self.modo_rfid:
            messagebox.showerror("Erro de Acesso", "Cartão não autorizado ou inválido.")
            self.entry_codigo.delete(0, tk.END)
            
    def verificar_leitor_rfid_periodicamente(self):
        if self.modo_rfid:
            codigo_lido = self.carrinho.hardware.obter_cartao_lido()
            if codigo_lido:
                self.processar_validacao(codigo_lido)
        
        self.after_id = self.root.after(250, self.verificar_leitor_rfid_periodicamente)

    def executar(self):
        self.root.mainloop()
        return self.usuario, self.perfil