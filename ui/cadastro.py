import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from ui.theme import CORES, FONTES
from models.entities import UsuarioCartao  
import datetime

class TelaCadastroRFID:
    def __init__(self, carrinho, root_principal=None, callback_atualizar_usuarios=None):
        self.carrinho = carrinho
        self.root_principal = root_principal  
        self.callback_atualizar_usuarios = callback_atualizar_usuarios  
        self.id_cartao_lido = None
        self.modo_rfid = True

        self.root = tk.Tk()
        self.root.title("Cadastro RFID - CRDF")
        self.root.geometry("600x650") 
        self.root.configure(bg=CORES["fundo_principal"])
        self.root.resizable(False, False)
        self.centralizar_janela()
        self.setup_interface()
        

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

        try:
            self.crdf_icon_img = ImageTk.PhotoImage(Image.open("crdf_icon.png").resize((160, 160), Image.LANCZOS))
            tk.Label(frame_titulo_principal, image=self.crdf_icon_img, bg=CORES["fundo_principal"]).pack(side="left", padx=5)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar 'crdf_icon.png': {e}")
        
        frame_textos = tk.Frame(frame_titulo_principal, bg=CORES["fundo_principal"])
        frame_textos.pack(side="left", expand=True, fill="x", padx=10)
        
        tk.Label(frame_textos, text="CRDF", font=("Segoe UI", 48, "bold"), fg="white", bg=CORES["fundo_principal"]).pack(anchor="w")
        tk.Label(frame_textos, text="Controle de Retirada e", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(anchor="w")
        tk.Label(frame_textos, text="Devolução de Ferramentas", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(anchor="w")

        self.frame_entrada_alternavel = tk.Frame(main_frame, bg=CORES["fundo_principal"])
        self.frame_entrada_alternavel.pack(pady=20, fill="x", expand=True)
        
        self.frame_rfid_prompt = tk.Frame(self.frame_entrada_alternavel, bg=CORES["fundo_principal"])
        try:
            self.rfid_icon_img = ImageTk.PhotoImage(Image.open("rfid_icon.png").resize((100, 100), Image.LANCZOS))
            tk.Label(self.frame_rfid_prompt, image=self.rfid_icon_img, bg=CORES["fundo_principal"]).pack(pady=5)
        except: pass
        tk.Label(self.frame_rfid_prompt, text="Aproxime seu Token para Cadastro", font=("Segoe UI", 18, "bold"), fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(pady=10)

        self.frame_texto_prompt = tk.Frame(self.frame_entrada_alternavel, bg=CORES["fundo_principal"])
        tk.Label(self.frame_texto_prompt, text="Digite o código do seu cartão para cadastro", font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(pady=5)
        self.entry_codigo = tk.Entry(self.frame_texto_prompt, font=FONTES["botao"], justify="center", width=25,
                                     bg=CORES["fundo_tabela"], fg=CORES["texto_escuro"], relief="flat")
        self.entry_codigo.pack(pady=10, ipady=8)
        self.entry_codigo.bind("<Return>", self.validar_cadastro_manual)
        
        self.btn_alternar = tk.Button(main_frame, text="", font=FONTES["corpo"], command=self.alternar_modo_entrada, relief="flat", 
                                      bg=CORES["fundo_principal"], fg=CORES["destaque"], 
                                      activebackground=CORES["fundo_principal"], activeforeground="white", borderwidth=0)
        self.btn_alternar.pack()
        
        self.btn_cadastro = tk.Button(main_frame, text="CADASTRAR", font=FONTES["botao"], command=self.validar_cadastro_manual, 
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
            self.btn_cadastro.pack_forget()
        else:
            self.frame_rfid_prompt.pack_forget()
            self.frame_texto_prompt.pack(pady=10)
            self.btn_alternar.config(text="Ou, clique para Usar o Leitor RFID")
            self.btn_cadastro.pack(pady=20)
            self.entry_codigo.focus()

    def validar_cadastro_manual(self, event=None):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Por favor, digite o código do cartão para cadastro.")
            return
        self.processar_cadastro(codigo)

    def processar_cadastro(self, codigo):
        # Verifica se o ID já existe (não é novo usuário)
        usuario_existente = self.carrinho.validar_cartao(codigo)
        if usuario_existente:
            messagebox.showerror("Erro de Cadastro", f"ID de cartão '{codigo}' já cadastrado para o usuário '{usuario_existente.nome}'. Use outro token.", parent=self.root)
            self.entry_codigo.delete(0, tk.END)
            return
        
        # Se novo, abre popup para coletar nome, cargo, perfil
        self.id_cartao_lido = codigo
        if hasattr(self, 'after_id'): 
            self.root.after_cancel(self.after_id)
        
        messagebox.showinfo("Sucesso", f"ID '{codigo}' válido para cadastro. Agora, preencha os detalhes do usuário.", parent=self.root)
        self.mostrar_popup_detalhes_usuario()  # NOVO: Popup integrado aqui

    def mostrar_popup_detalhes_usuario(self):
        # Popup para nome, cargo, perfil (ID pré-preenchido)
        popup = tk.Toplevel(self.root)  # Filho do modal de cadastro
        popup.title("Detalhes do Novo Usuário")
        popup.geometry("450x450")
        popup.resizable(False, False)
        popup.transient(self.root)  # Modal em relação à tela de cadastro
        popup.grab_set()
        popup.configure(bg=CORES["fundo_secundario"])

        # Título
        tk.Label(popup, text="SENAI", font=("Segoe UI", 24, "bold"), fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(20, 0))
        tk.Label(popup, text="DETALHES DO USUÁRIO", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(0, 20))

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
                combo_perfil.set("aluno")  # Default aluno
                entries[campo] = combo_perfil
            else:
                entry = ttk.Entry(form_frame, width=25)
                entry.grid(row=i, column=1, sticky="ew", pady=8, padx=5)
                entries[campo] = entry

        # Pré-preencher ID do Cartão (readonly)
        if self.id_cartao_lido:
            entries["ID do Cartão:"].insert(0, self.id_cartao_lido)
            entries["ID do Cartão:"].config(state="readonly")

        def salvar_novo_usuario():
            id_cartao = entries["ID do Cartão:"].get().strip()
            nome = entries["Nome:"].get().strip()
            cargo = entries["Cargo:"].get().strip()
            perfil = entries["Perfil:"].get().strip()

            # Validação: Todos os campos obrigatórios
            if not all([id_cartao, nome, cargo, perfil]):
                messagebox.showerror("Erro de Validação", "Preencha **todos** os campos para cadastrar o usuário!\n- Nome e Cargo são obrigatórios.\n- Perfil deve ser selecionado.", parent=popup)
                return

            # Cria e salva o usuário
            usuario = UsuarioCartao(id=id_cartao, nome=nome, cargo=cargo, perfil=perfil, 
                                    data_cadastro=datetime.datetime.now().isoformat(), ativo=True)
            try:
                self.carrinho.db.adicionar_usuario(usuario)
                messagebox.showinfo("Cadastro Concluído!", f"Usuário '{nome}' cadastrado com sucesso!\nID: {id_cartao} | Perfil: {perfil}", parent=popup)
                popup.destroy()
                self.root.destroy()  # Fecha o modal de cadastro
                # Atualiza lista na interface principal (se callback fornecido)
                if self.callback_atualizar_usuarios:
                    self.callback_atualizar_usuarios()
            except Exception as e:
                messagebox.showerror("Erro no Cadastro", f"Falha ao salvar usuário: {e}\nVerifique os logs.", parent=popup)
                logging.error(f"Erro ao cadastrar usuário {nome}: {e}")

        # Botões
        frame_botoes = tk.Frame(popup, bg=CORES["fundo_secundario"])
        frame_botoes.pack(pady=30)

        btn_salvar = tk.Button(frame_botoes, text="Salvar Usuário", font=FONTES["botao"], bg=CORES["sucesso"],
                               fg="white", relief="flat", padx=20, pady=8, borderwidth=0, command=salvar_novo_usuario)
        btn_salvar.pack(side="left", padx=10)

        btn_cancelar = tk.Button(frame_botoes, text="Cancelar Cadastro", font=FONTES["botao"], bg=CORES["cancelar"],
                                 fg="white", relief="flat", padx=20, pady=8, borderwidth=0, 
                                 command=lambda: [popup.destroy(), self.root.destroy()])
        btn_cancelar.pack(side="left", padx=10)

    def verificar_leitor_rfid_periodicamente(self):
        if self.modo_rfid:
            try:
                codigo_lido = self.carrinho.hardware.ler_rfid()
                if codigo_lido:
                    self.processar_cadastro(codigo_lido)
            except AttributeError:
                pass  # Hardware não configurado
        
        self.after_id = self.root.after(250, self.verificar_leitor_rfid_periodicamente)

    def executar(self):
        # Ativa verificação RFID se modo RFID (descomente para auto-leitura)
        # self.verificar_leitor_rfid_periodicamente()
        
        if self.root_principal:
            self.root.transient(self.root_principal)  # Modal em relação à janela principal
            self.root.grab_set()  # Bloqueia interação com outras janelas
        
        self.root.mainloop()
        
        # Verificação para evitar destruição dupla
        if self.root.winfo_exists():
            self.root.destroy()
        
        return self.id_cartao_lido  # Retorna ID se precisar (opcional agora)