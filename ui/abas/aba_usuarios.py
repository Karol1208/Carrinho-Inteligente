import customtkinter as ctk
from tkinter import messagebox, ttk
import datetime
import sqlite3
import logging
from ui.theme import CORES, FONTES
from ui.components.glass_card import GlassCard
from ui.components.tabela_pro import TabelaPRO

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

        # TabelaPRO - Layout global sofisticado
        self.tabela_usuarios = TabelaPRO(
            lista_card,
            columns=['ID', 'Nome', 'Cargo', 'Perfil', 'Data Cadastro'],
            col_widths=[1, 3, 2, 2, 2],
            show_actions=False,
            on_select=self._on_usuario_select
        )
        self.tabela_usuarios.pack(fill='both', expand=True, padx=20, pady=20)
        
        self._usuario_selecionado = None

    def _on_usuario_select(self, row_data):
        self._usuario_selecionado = row_data

    def atualizar_lista_usuarios(self):
        usuarios = self.carrinho.db.listar_usuarios()
        data = []
        for usuario in usuarios:
            data_cadastro = usuario.data_cadastro or "N/A"
            try:
                data_cadastro = datetime.datetime.fromisoformat(data_cadastro).strftime("%d/%m/%Y %H:%M")
            except:
                pass
            data.append([
                usuario.id, usuario.nome, usuario.cargo, usuario.perfil, data_cadastro
            ])
        self.tabela_usuarios.carregar(data)
        self._usuario_selecionado = None

    def remover_usuario_selecionado(self):
        if not self._usuario_selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para remover clicando na tabela!")
            return

        usuario_id = self._usuario_selecionado[0]
        nome_usuario = self._usuario_selecionado[1]

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