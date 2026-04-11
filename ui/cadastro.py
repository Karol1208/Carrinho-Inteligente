import customtkinter as ctk
from tkinter import messagebox, ttk
import logging
import datetime
from PIL import Image
from ui.theme import CORES, FONTES
from models.entities import UsuarioCartao
from ui.components.glass_card import GlassCard

class TelaCadastroRFID:
    def __init__(self, carrinho, root_principal=None, callback_atualizar_usuarios=None):
        self.carrinho = carrinho
        self.root_principal = root_principal
        self.callback_atualizar_usuarios = callback_atualizar_usuarios
        self.id_cartao_lido = None
        self.modo_rfid = True 
        self.after_tasks = []

        # Janela Modal com CustomTkinter
        self.root = ctk.CTkToplevel(self.root_principal)
        self.root.title("Cadastro de Usuário - CRDF")
        self.root.geometry("600x700")
        self.root.configure(fg_color=CORES["fundo_principal"])
        
        self.root.transient(self.root_principal)
        self.root.grab_set()

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

    def setup_interface(self):
        # Container Principal
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=30, pady=30)

        # Cabeçalho
        ctk.CTkLabel(container, text="SENAI", font=FONTES["titulo"], text_color=CORES["texto_claro"]).pack()
        ctk.CTkLabel(container, text="NOVO COLABORADOR", font=FONTES["subtitulo"], text_color=CORES["destaque"]).pack(pady=(0, 20))

        # Card de Entrada
        self.input_card = GlassCard(container)
        self.input_card.pack(fill="x", pady=20)

        self.label_instrucao = ctk.CTkLabel(
            self.input_card, 
            text="Aproxime a Tag RFID", 
            font=FONTES["subtitulo"],
            text_color="white"
        )
        self.label_instrucao.pack(pady=(20, 5))

        self.label_status = ctk.CTkLabel(
            self.input_card, 
            text="Aguardando leitura do sensor...", 
            font=FONTES["corpo"],
            text_color=CORES["texto_muted"]
        )
        self.label_status.pack(pady=(0, 20))

        # Campo de Entrada Manual (Escondido initially)
        self.entry_codigo = ctk.CTkEntry(
            self.input_card, 
            placeholder_text="Ou digite o código manualmente",
            width=300,
            height=45,
            font=FONTES["corpo"],
            justify="center"
        )
        self.entry_codigo.bind("<Return>", lambda e: self.validar_cadastro_manual())

        # Botões de Alternância
        self.btn_alternar = ctk.CTkButton(
            container,
            text="⌨️ Digitar Código Manualmente",
            fg_color="transparent",
            text_color=CORES["destaque"],
            hover_color=CORES["glass_borda"],
            command=self.alternar_modo
        )
        self.btn_alternar.pack(pady=10)

        # Botão Cadastrar (Aparece no modo manual)
        self.btn_confirmar = ctk.CTkButton(
            container,
            text="PROSSEGUIR COM CADASTRO",
            fg_color=CORES["sucesso"],
            font=FONTES["botao"],
            height=50,
            command=self.validar_cadastro_manual
        )

    def alternar_modo(self):
        self.modo_rfid = not self.modo_rfid
        if self.modo_rfid:
            self.entry_codigo.pack_forget()
            self.btn_confirmar.pack_forget()
            self.label_instrucao.configure(text="Aproxime a Tag RFID")
            self.btn_alternar.configure(text="⌨️ Digitar Código Manualmente")
        else:
            self.entry_codigo.pack(pady=10)
            self.btn_confirmar.pack(pady=20, fill="x")
            self.label_instrucao.configure(text="Entrada Manual")
            self.btn_alternar.configure(text="📡 Usar Leitor RFID")
            self.entry_codigo.focus()

    def safe_destroy(self):
        self.limpar_tasks()
        # Remove o callback antes de fechar
        try:
            self.carrinho.remover_callback_rfid(self.on_rfid_read)
        except:
            pass
        self.root.destroy()

    def on_rfid_read(self, codigo):
        """Trata o evento de leitura de RFID disparado pelo backend."""
        if not self.root.winfo_exists() or not self.modo_rfid:
            return
        
        # Agenda para o loop principal do Tkinter
        self.root.after(0, lambda: self.processar_leitura_rfid(codigo))

    def processar_leitura_rfid(self, codigo):
        self.label_status.configure(text=f"ID Detectado: {codigo}", text_color=CORES["sucesso"])
        self.processar_cadastro(codigo)

    def processar_cadastro(self, codigo):
        existente = self.carrinho.validar_cartao(codigo)
        if existente:
            messagebox.showerror("Erro", f"Tag {codigo} já pertence a {existente.nome}")
            self.safe_destroy()
            return
        
        self.id_cartao_lido = codigo
        self.mostrar_popup_detalhes()

    def validar_cadastro_manual(self):
        cod = self.entry_codigo.get().strip()
        if not cod:
            messagebox.showwarning("Aviso", "Digite um código válido")
            return
        self.processar_cadastro(cod)

    def mostrar_popup_detalhes(self):
        # Reutiliza a janela atual ou cria um novo card por cima
        for child in self.root.winfo_children(): child.destroy()
        
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=40, pady=30)

        ctk.CTkLabel(container, text="DETALHES DO COLABORADOR", font=FONTES["subtitulo"]).pack(pady=20)
        
        form_card = GlassCard(container)
        form_card.pack(fill="both", expand=True, pady=10)

        campos = ["ID Cartão", "Nome Completo", "Cargo", "Perfil"]
        self.entries = {}

        for campo in campos:
            ctk.CTkLabel(form_card, text=campo, font=FONTES["corpo"], text_color=CORES["texto_muted"]).pack(anchor="w", padx=25, pady=(15, 0))
            if campo == "Perfil":
                entry = ctk.CTkComboBox(form_card, values=["admin", "aluno"], height=40)
                entry.set("aluno")
            else:
                entry = ctk.CTkEntry(form_card, height=40)
                if campo == "ID Cartão":
                    entry.insert(0, self.id_cartao_lido)
                    entry.configure(state="readonly")
            
            entry.pack(fill="x", padx=20, pady=(5, 5))
            self.entries[campo] = entry

        def salvar():
            nome = self.entries["Nome Completo"].get()
            cargo = self.entries["Cargo"].get()
            perfil = self.entries["Perfil"].get()

            if not nome or not cargo:
                messagebox.showwarning("Aviso", "Preencha todos os campos")
                return

            u = UsuarioCartao(
                id=self.id_cartao_lido, 
                nome=nome, 
                cargo=cargo, 
                perfil=perfil,
                data_cadastro=datetime.datetime.now().isoformat(), 
                ativo=True
            )
            try:
                self.carrinho.db.adicionar_usuario(u)
                messagebox.showinfo("Sucesso", f"Usuário {nome} cadastrado!")
                if self.callback_atualizar_usuarios: self.callback_atualizar_usuarios()
                self.safe_destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(pady=30)
        ctk.CTkButton(btn_row, text="SALVAR", fg_color=CORES["sucesso"], height=45, command=salvar).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="CANCELAR", fg_color="transparent", border_width=1, height=45, command=self.safe_destroy).pack(side="left", padx=10)

    def executar(self):
        # Inscreve-se no evento de leitura no backend
        self.carrinho.registrar_callback_rfid(self.on_rfid_read)
        self.root.wait_window(self.root)