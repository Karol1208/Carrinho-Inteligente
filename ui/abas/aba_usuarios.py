# ui/abas/aba_usuarios.py

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import logging
import sqlite3
from ui.theme import CORES, FONTES 

class AbaUsuarios(ttk.Frame):
    """Frame que gerencia o cadastro e listagem de usuários."""
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent)
        self.carrinho = carrinho_controller
        self.app = app_controller

        self.setup_widgets()
        self.atualizar_lista_usuarios()

    def setup_widgets(self):
        style = ttk.Style()
        
        style.configure("Sucesso.TButton",
                        font=FONTES["botao"],
                        background=CORES["sucesso"],
                        foreground=CORES["texto_claro"])
        style.map("Sucesso.TButton",
                  background=[('active', '#27ae60')])

        cor_vermelha = CORES.get("cancelar", "#e74c3c") 
        cor_vermelha_active = CORES.get("cancelar_active", "#c0392b") 
        
        style.configure("Remover.TButton",
                        font=FONTES["botao"],
                        background=cor_vermelha,
                        foreground=CORES["texto_claro"])
        style.map("Remover.TButton",
                  background=[('active', cor_vermelha_active)])

        frame_acoes = ttk.LabelFrame(self, text="Ações", padding=10)
        frame_acoes.pack(fill='x', padx=10, pady=5)

        ttk.Button(
            frame_acoes,
            text="Cadastrar Novo Usuário via RFID",
            command=self.app.abrir_tela_cadastro_rfid,
            style="Sucesso.TButton"  
        ).pack(pady=10)

        frame_lista = ttk.LabelFrame(self, text="Usuários Cadastrados", padding=10)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Nome', 'Cargo', 'Perfil', 'Data Cadastro')
        self.tree_usuarios = ttk.Treeview(frame_lista, columns=columns, show='headings', height=10)

        for col in columns:
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=150)

        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scrollbar.set)
        self.tree_usuarios.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        frame_botoes_lista = ttk.Frame(frame_lista)
        frame_botoes_lista.pack(fill='x', pady=5)

        ttk.Button(
            frame_botoes_lista, 
            text="Atualizar Lista", 
            command=self.atualizar_lista_usuarios,
            style="Sucesso.TButton"  
        ).pack(side='left', padx=5)
        
        ttk.Button(
            frame_botoes_lista, 
            text="Remover Selecionado", 
            command=self.remover_usuario_selecionado,
            style="Remover.TButton"  
        ).pack(side='left', padx=5)

    def atualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)

        usuarios = self.carrinho.db.listar_usuarios()
        for usuario in usuarios:
            data_cadastro = usuario.data_cadastro or "N/A"
            try:
                data_cadastro = datetime.datetime.fromisoformat(data_cadastro).strftime("%d/%m/%Y %H:%M")
            except (ValueError, AttributeError):
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

        if messagebox.askyesno("Confirmar", f"Deseja realmente remover o usuário {nome_usuario}? (Isso apenas o desativará no sistema)"):
            try:
                conn = sqlite3.connect(self.carrinho.db.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE usuarios SET ativo = 0 WHERE id = ?', (usuario_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", f"Usuário {nome_usuario} removido (desativado) com sucesso!")
                self.atualizar_lista_usuarios()
                self.app.aba_inventario.atualizar_combo_usuarios_pendencias()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover usuário: {e}")
                logging.error(f"Erro ao remover usuário {usuario_id}: {e}")