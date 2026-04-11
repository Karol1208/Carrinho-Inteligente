import customtkinter as ctk
from tkinter import messagebox, ttk
import datetime
import sqlite3
import logging
from ui.theme import CORES, FONTES
from ui.components.glass_card import GlassCard

class AbaUsuarios(ctk.CTkFrame):
    """Frame que gerencia o cadastro e listagem de usuários."""
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.carrinho = carrinho_controller
        self.app = app_controller

        self.setup_widgets()
        self.atualizar_lista_usuarios()

    def setup_widgets(self):
        # 1. Card de Ações
        acoes_card = GlassCard(self)
        acoes_card.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(acoes_card, text="👤 Gestão de Acesso", font=FONTES["subtitulo"]).pack(side="left", padx=20, pady=20)
        
        ctk.CTkButton(
            acoes_card,
            text="+ CADASTRAR NOVO USUÁRIO (RFID)",
            fg_color=CORES["sucesso"],
            hover_color="#27ae60",
            font=FONTES["botao"],
            height=40,
            command=self.app.abrir_tela_cadastro_rfid
        ).pack(side="right", padx=20, pady=20)

        # 2. Card da Lista
        lista_card = GlassCard(self)
        lista_card.pack(fill="both", expand=True, padx=10, pady=10)

        # Barra de Ferramentas da Lista
        toolbar = ctk.CTkFrame(lista_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(toolbar, text="Lista de Colaboradores", font=FONTES["corpo"]).pack(side="left")

        ctk.CTkButton(
            toolbar, 
            text="🗑 Remover Selecionado", 
            width=150,
            fg_color=CORES["cancelar"],
            hover_color="#c0392b",
            command=self.remover_usuario_selecionado
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            toolbar, 
            text="🔄 Atualizar", 
            width=100,
            fg_color=CORES["destaque"],
            command=self.atualizar_lista_usuarios
        ).pack(side="right", padx=5)

        # Treeview (Estilo herdado pelo Header do Tkinter, mas com as cores ajustadas)
        columns = ('ID', 'Nome', 'Cargo', 'Perfil', 'Data Cadastro')
        self.tree_usuarios = ttk.Treeview(lista_card, columns=columns, show='headings')

        for col in columns:
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=150)

        self.tree_usuarios.pack(fill='both', expand=True, padx=20, pady=20)

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
            self.tree_usuarios.insert('', 'end', values=(
                usuario.id, usuario.nome, usuario.cargo, usuario.perfil, data_cadastro
            ))

    def remover_usuario_selecionado(self):
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um usuário para remover!")
            return

        item = self.tree_usuarios.item(selection[0])
        usuario_id = item['values'][0]
        nome_usuario = item['values'][1]

        if messagebox.askyesno("Confirmar", f"Deseja realmente desativar o usuário {nome_usuario}?"):
            try:
                conn = sqlite3.connect(self.carrinho.db.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE usuarios SET ativo = 0 WHERE id = ?', (usuario_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", f"Usuário {nome_usuario} desativado.")
                self.atualizar_lista_usuarios()
                if hasattr(self.app, 'aba_inventario'):
                    self.app.aba_inventario.atualizar_combo_usuarios_pendencias()
            except Exception as e:
                messagebox.showerror("Erro", str(e))