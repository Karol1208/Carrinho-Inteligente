# Em ui/cadastro.py (Versão Final Mesclada)

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import datetime
from PIL import Image, ImageTk

# Importações absolutas para consistência
from ui.theme import CORES, FONTES
from models.entities import UsuarioCartao

class TelaCadastroRFID:
    def __init__(self, carrinho, root_principal=None, callback_atualizar_usuarios=None):
        self.carrinho = carrinho
        self.root_principal = root_principal
        self.callback_atualizar_usuarios = callback_atualizar_usuarios
        self.id_cartao_lido = None
        self.modo_rfid = True # Inicia no modo RFID por padrão

        # Usa Toplevel para funcionar como um pop-up sobre a janela principal
        self.root = tk.Toplevel(self.root_principal)
        self.root.title("Cadastro de Usuário - CRDF")
        self.root.geometry("600x650")
        self.root.configure(bg=CORES["fundo_principal"])
        self.root.resizable(False, False)
        
        # Comandos para tornar a janela um modal verdadeiro
        self.root.transient(self.root_principal)
        self.root.grab_set()

        self.centralizar_janela()
        self.setup_interface()
        
        # Inicia a verificação do hardware em segundo plano
        self.verificar_hardware_periodicamente()

    def centralizar_janela(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root_principal.winfo_x() + (self.root_principal.winfo_width() // 2)) - (width // 2)
        y = (self.root_principal.winfo_y() + (self.root_principal.winfo_height() // 2)) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_interface(self):
        # Interface completa da versão do seu colega
        main_frame = tk.Frame(self.root, bg=CORES["fundo_principal"])
        main_frame.pack(expand=True, fill="both")

        # Layout superior
        tk.Label(main_frame, text="SENAI", font=("Segoe UI", 20, "bold"), fg="white", bg=CORES["fundo_principal"]).pack(pady=(20, 10))
        
        frame_titulo_principal = tk.Frame(main_frame, bg=CORES["fundo_principal"])
        frame_titulo_principal.pack(pady=20, padx=30, fill="x")
        
        frame_textos = tk.Frame(frame_titulo_principal, bg=CORES["fundo_principal"])
        frame_textos.pack(side="left", expand=True, fill="x", padx=10)
        
        tk.Label(frame_textos, text="CRDF", font=("Segoe UI", 48, "bold"), fg="white", bg=CORES["fundo_principal"]).pack(anchor="w")
        tk.Label(frame_textos, text="Cadastro de Novo Usuário", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(anchor="w")

        self.frame_entrada_alternavel = tk.Frame(main_frame, bg=CORES["fundo_principal"])
        self.frame_entrada_alternavel.pack(pady=20, fill="x", expand=True)
        
        # Frame para o modo RFID
        self.frame_rfid_prompt = tk.Frame(self.frame_entrada_alternavel, bg=CORES["fundo_principal"])
        tk.Label(self.frame_rfid_prompt, text="Aproxime a nova TAG", font=("Segoe UI", 18, "bold"), fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(pady=10)
        
        self.label_status_leitura = tk.Label(self.frame_rfid_prompt, text="Aguardando leitura...", font=FONTES["corpo"], fg=CORES["destaque"], bg=CORES["fundo_principal"])
        self.label_status_leitura.pack(pady=5)

        # Frame para o modo de digitação manual
        self.frame_texto_prompt = tk.Frame(self.frame_entrada_alternavel, bg=CORES["fundo_principal"])
        tk.Label(self.frame_texto_prompt, text="Digite o código do cartão para cadastro", font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_principal"]).pack(pady=5)
        self.entry_codigo = tk.Entry(self.frame_texto_prompt, font=FONTES["botao"], justify="center", width=25,
                                     bg=CORES["fundo_tabela"], fg=CORES["texto_escuro"], relief="flat")
        self.entry_codigo.pack(pady=10, ipady=8)
        self.entry_codigo.bind("<Return>", self.validar_cadastro_manual)
        
        # Botões de controle
        self.btn_alternar = tk.Button(main_frame, text="", font=FONTES["corpo"], command=self.alternar_modo_entrada, relief="flat", 
                                       bg=CORES["fundo_principal"], fg=CORES["destaque"], 
                                       activebackground=CORES["fundo_principal"], activeforeground="white", borderwidth=0)
        self.btn_alternar.pack()
        
        self.btn_cadastro = tk.Button(main_frame, text="CADASTRAR", font=FONTES["botao"], command=self.validar_cadastro_manual, 
                                      bg=CORES["sucesso"], fg="white", relief="flat", padx=40, pady=10, borderwidth=0)
        
        self.atualizar_modo_entrada()

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
            messagebox.showwarning("Aviso", "Por favor, digite o código do cartão para cadastro.", parent=self.root)
            return
        self.processar_cadastro(codigo)

    def verificar_hardware_periodicamente(self):
        if self.modo_rfid:
            try:
                codigo_lido = self.carrinho.hardware.ler_input_hardware()
                if codigo_lido:
                    self.label_status_leitura.config(text=f"Tag lida: {codigo_lido}", fg="lightgreen")
                    self.processar_cadastro(codigo_lido)
                    return
            except AttributeError:
                self.label_status_leitura.config(text="Hardware não compatível.", fg="red")
                return
        
        self.after_id = self.root.after(250, self.verificar_hardware_periodicamente)

    def processar_cadastro(self, codigo):
        if hasattr(self, 'after_id'):
            self.root.after_cancel(self.after_id)

        usuario_existente = self.carrinho.validar_cartao(codigo)
        if usuario_existente:
            messagebox.showerror("Erro de Cadastro", f"A tag '{codigo}' já está cadastrada para o usuário '{usuario_existente.nome}'.", parent=self.root)
            self.root.destroy()
            return
        
        self.id_cartao_lido = codigo
        self.mostrar_popup_detalhes_usuario()

    def mostrar_popup_detalhes_usuario(self):
        popup = tk.Toplevel(self.root)
        popup.title("Detalhes do Novo Usuário")
        popup.geometry("450x450")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg=CORES["fundo_secundario"])

        tk.Label(popup, text="SENAI", font=("Segoe UI", 24, "bold"), fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(20, 0))
        tk.Label(popup, text="DETALHES DO USUÁRIO", font=FONTES["subtitulo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"]).pack(pady=(0, 20))

        form_frame = tk.Frame(popup, bg=CORES["fundo_secundario"])
        form_frame.pack(padx=30, pady=10)

        campos = ["ID do Cartão:", "Nome:", "Cargo:", "Perfil:"]
        entries = {}

        for i, campo in enumerate(campos):
            lbl = tk.Label(form_frame, text=campo, font=FONTES["corpo"], fg=CORES["texto_claro"], bg=CORES["fundo_secundario"])
            lbl.grid(row=i, column=0, sticky="w", pady=8, padx=5)
            
            if campo == "Perfil:":
                combo_perfil = ttk.Combobox(form_frame, values=["admin", "aluno"], width=23, state="readonly", font=FONTES["corpo"])
                combo_perfil.grid(row=i, column=1, sticky="ew", pady=8, padx=5)
                combo_perfil.set("aluno")
                entries[campo] = combo_perfil
            else:
                entry = ttk.Entry(form_frame, width=25, font=FONTES["corpo"])
                entry.grid(row=i, column=1, sticky="ew", pady=8, padx=5)
                entries[campo] = entry

        if self.id_cartao_lido:
            entries["ID do Cartão:"].insert(0, self.id_cartao_lido)
            entries["ID do Cartão:"].config(state="readonly")

        def salvar_novo_usuario():
            id_cartao = entries["ID do Cartão:"].get().strip()
            nome = entries["Nome:"].get().strip()
            cargo = entries["Cargo:"].get().strip()
            perfil = entries["Perfil:"].get().strip()

            if not all([id_cartao, nome, cargo, perfil]):
                messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios!", parent=popup)
                return

            usuario = UsuarioCartao(id=id_cartao, nome=nome, cargo=cargo, perfil=perfil,
                                      data_cadastro=datetime.datetime.now().isoformat(), ativo=True)
            try:
                self.carrinho.db.adicionar_usuario(usuario)
                messagebox.showinfo("Cadastro Concluído!", f"Usuário '{nome}' cadastrado com sucesso!", parent=self.root)
                popup.destroy()
                self.root.destroy()
                
                if self.callback_atualizar_usuarios:
                    self.callback_atualizar_usuarios()
            except Exception as e:
                messagebox.showerror("Erro no Cadastro", f"Falha ao salvar usuário: {e}", parent=popup)
                logging.error(f"Erro ao cadastrar usuário {nome}: {e}")

        frame_botoes = tk.Frame(popup, bg=CORES["fundo_secundario"])
        frame_botoes.pack(pady=30)

        btn_salvar = tk.Button(frame_botoes, text="Salvar Usuário", font=FONTES["botao"], bg=CORES["sucesso"],
                               fg="white", relief="flat", padx=20, pady=8, borderwidth=0, command=salvar_novo_usuario)
        btn_salvar.pack(side="left", padx=10)

        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", font=FONTES["botao"], bg=CORES["cancelar"],
                                 fg="white", relief="flat", padx=20, pady=8, borderwidth=0, command=popup.destroy)
        btn_cancelar.pack(side="left", padx=10)

    def executar(self):
        self.root.wait_window(self.root)