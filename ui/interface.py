import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import datetime
import json
import logging
from typing import Optional

from core.cart import CarrinhoInteligenteAvancado
from models.entities import Peca, UsuarioCartao

class InterfaceGraficaCarrinho:
    def __init__(self, carrinho: 'CarrinhoInteligenteAvancado' = None):
        if carrinho:
            self.carrinho = carrinho
        else:
            self.carrinho = CarrinhoInteligenteAvancado()
        self.root = tk.Tk()
        self.root.title("Sistema Carrinho Inteligente - Oficina Mecânica")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        self.usuario_atual = None
        self.alertas_exibidos = set()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))

        self.setup_interface()
        self.atualizar_status_periodico()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def setup_interface(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Aba Principal (atualizada para peças)
        frame_principal = ttk.Frame(notebook)
        notebook.add(frame_principal, text="Controle Principal")
        self.setup_aba_principal(frame_principal)

        # Aba de Usuários
        frame_usuarios = ttk.Frame(notebook)
        notebook.add(frame_usuarios, text="Gerenciar Usuários")
        self.setup_aba_usuarios(frame_usuarios)

        # Aba de Histórico
        frame_historico = ttk.Frame(notebook)
        notebook.add(frame_historico, text="Histórico")
        self.setup_aba_historico(frame_historico)

        # Aba de Monitoramento
        frame_monitor = ttk.Frame(notebook)
        notebook.add(frame_monitor, text="Monitoramento")
        self.setup_aba_monitoramento(frame_monitor)

        # Aba Inventário e Pendências
        frame_inventario = ttk.Frame(notebook)
        notebook.add(frame_inventario, text="Inventário e Pendências")
        self.setup_aba_inventario(frame_inventario)

    def setup_aba_principal(self, parent):
        # Frame superior para entrada do cartão
        frame_cartao = ttk.LabelFrame(parent, text="Acesso por Cartão", padding=10)
        frame_cartao.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_cartao, text="Código do Cartão:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_cartao = ttk.Entry(frame_cartao, font=('Arial', 12), width=20)
        self.entry_cartao.grid(row=0, column=1, padx=5, pady=5)
        self.entry_cartao.bind('<Return>', self.processar_cartao)

        ttk.Button(frame_cartao, text="Validar Cartão", command=self.processar_cartao).grid(row=0, column=2, padx=5)

        self.label_usuario_atual = ttk.Label(frame_cartao, text="Nenhum usuário identificado", foreground='red')
        self.label_usuario_atual.grid(row=1, column=0, columnspan=3, pady=5)

        # Frame das gavetas
        frame_gavetas = ttk.LabelFrame(parent, text="Controle das Gavetas", padding=10)
        frame_gavetas.pack(fill='both', expand=True, padx=10, pady=5)

        self.frames_gavetas = {}
        self.labels_status_gavetas = {}
        self.botoes_gavetas = {}
        self.info_labels_gavetas = {}  

        for i in range(1, 6):
            frame_gaveta = ttk.LabelFrame(frame_gavetas, text=f"Gaveta {i}", padding=5)
            frame_gaveta.grid(row=(i-1)//3, column=(i-1)%3, padx=5, pady=5, sticky='nsew')

            status_label = ttk.Label(frame_gaveta, text="FECHADA", foreground='green', font=('Arial', 10, 'bold'))
            status_label.pack(pady=5)

            btn_toggle = ttk.Button(frame_gaveta, text="Abrir", command=lambda g=i: self.toggle_gaveta_com_pecas(g))
            btn_toggle.pack(pady=5)

            info_label = ttk.Label(frame_gaveta, text="--", font=('Arial', 8))
            info_label.pack(pady=2)

            self.frames_gavetas[i] = frame_gaveta
            self.labels_status_gavetas[i] = status_label
            self.botoes_gavetas[i] = btn_toggle
            self.info_labels_gavetas[i] = info_label

        for i in range(3):
            frame_gavetas.grid_columnconfigure(i, weight=1)
        for i in range(2):
            frame_gavetas.grid_rowconfigure(i, weight=1)

    def setup_aba_usuarios(self, parent):
        frame_add = ttk.LabelFrame(parent, text="Cadastrar Novo Usuário", padding=10)
        frame_add.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_add, text="ID do Cartão:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_novo_id = ttk.Entry(frame_add, width=15)
        self.entry_novo_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_add, text="Nome:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.entry_novo_nome = ttk.Entry(frame_add, width=20)
        self.entry_novo_nome.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_add, text="Cargo:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.combo_cargo = ttk.Combobox(frame_add, values=["Professor", "Supervisor", "Líder", "Aluno"], width=15)
        self.combo_cargo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(frame_add, text="Cadastrar Usuário", command=self.cadastrar_usuario).grid(row=1, column=2, columnspan=2, padx=5, pady=5)

        # Lista de usuários
        frame_lista = ttk.LabelFrame(parent, text="Usuários Cadastrados", padding=10)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Nome', 'Cargo', 'Data Cadastro')
        self.tree_usuarios = ttk.Treeview(frame_lista, columns=columns, show='headings', height=10)

        for col in columns:
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=150)

        scrollbar_usuarios = ttk.Scrollbar(frame_lista, orient='vertical', command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scrollbar_usuarios.set)

        self.tree_usuarios.pack(side='left', fill='both', expand=True)
        scrollbar_usuarios.pack(side='right', fill='y')

        frame_acoes = ttk.Frame(frame_lista)
        frame_acoes.pack(fill='x', pady=5)

        ttk.Button(frame_acoes, text="Atualizar Lista", command=self.atualizar_lista_usuarios).pack(side='left', padx=5)
        ttk.Button(frame_acoes, text="Remover Selecionado", command=self.remover_usuario_selecionado).pack(side='left', padx=5)

        self.atualizar_lista_usuarios()

    def setup_aba_historico(self, parent):
        frame_historico = ttk.LabelFrame(parent, text="Histórico de Eventos", padding=10)
        frame_historico.pack(fill='both', expand=True, padx=10, pady=5)

        columns_hist = ('Data/Hora', 'Gaveta', 'Usuário', 'Ação', 'Status')
        self.tree_historico = ttk.Treeview(frame_historico, columns=columns_hist, show='headings', height=15)

        for col in columns_hist:
            self.tree_historico.heading(col, text=col)
            self.tree_historico.column(col, width=150)

        scrollbar_hist = ttk.Scrollbar(frame_historico, orient='vertical', command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar_hist.set)

        self.tree_historico.pack(side='left', fill='both', expand=True)
        scrollbar_hist.pack(side='right', fill='y')

        ttk.Button(frame_historico, text="Atualizar Histórico", command=self.atualizar_historico).pack(pady=5)

        self.atualizar_historico()

    def setup_aba_monitoramento(self, parent):
        frame_status = ttk.LabelFrame(parent, text="Status do Sistema", padding=10)
        frame_status.pack(fill='x', padx=10, pady=5)

        self.label_sistema_status = ttk.Label(frame_status, text="Sistema: ATIVO", foreground='green', font=('Arial', 12, 'bold'))
        self.label_sistema_status.pack(pady=5)

        frame_alertas = ttk.LabelFrame(parent, text="Alertas Ativos", padding=10)
        frame_alertas.pack(fill='both', expand=True, padx=10, pady=5)

        self.text_alertas = scrolledtext.ScrolledText(frame_alertas, height=10, width=80)
        self.text_alertas.pack(fill='both', expand=True)

        frame_controles = ttk.LabelFrame(parent, text="Controles do Sistema", padding=10)
        frame_controles.pack(fill='x', padx=10, pady=5)

        ttk.Button(frame_controles, text="Fechar Todas as Gavetas", command=self.fechar_todas_gavetas).pack(side='left', padx=5)
        ttk.Button(frame_controles, text="Limpar Alertas", command=self.limpar_alertas).pack(side='left', padx=5)
        ttk.Button(frame_controles, text="Exportar Logs", command=self.exportar_logs).pack(side='left', padx=5)

    def setup_aba_inventario(self, parent):
        # Frame superior: Gerenciar Peças
        frame_gerenciar = ttk.LabelFrame(parent, text="Gerenciar Peças (Inventário)", padding=10)
        frame_gerenciar.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_gerenciar, text="Nome:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_peca_nome = ttk.Entry(frame_gerenciar, width=20)
        self.entry_peca_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_gerenciar, text="Descrição:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.entry_peca_desc = ttk.Entry(frame_gerenciar, width=30)
        self.entry_peca_desc.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_gerenciar, text="Gaveta ID (1-5):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_peca_gaveta = ttk.Entry(frame_gerenciar, width=10)
        self.entry_peca_gaveta.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_gerenciar, text="Quantidade Disponível:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_peca_qtd = ttk.Entry(frame_gerenciar, width=10)
        self.entry_peca_qtd.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(frame_gerenciar, text="Adicionar/Atualizar Peça", command=self.cadastrar_peca).grid(row=1, column=4, padx=5, pady=5)

        # Lista de todas as peças
        frame_lista_pecas = ttk.LabelFrame(parent, text="Todas as Peças", padding=10)
        frame_lista_pecas.pack(fill='both', expand=True, padx=10, pady=5)

        columns_pecas = ('ID', 'Nome', 'Descrição', 'Gaveta', 'Qtd Disponível')
        self.tree_pecas = ttk.Treeview(frame_lista_pecas, columns=columns_pecas, show='headings', height=8)

        for col in columns_pecas:
            self.tree_pecas.heading(col, text=col)
            self.tree_pecas.column(col, width=120)

        scrollbar_pecas = ttk.Scrollbar(frame_lista_pecas, orient='vertical', command=self.tree_pecas.yview)
        self.tree_pecas.configure(yscrollcommand=scrollbar_pecas.set)

        self.tree_pecas.pack(side='left', fill='both', expand=True)
        scrollbar_pecas.pack(side='right', fill='y')

        ttk.Button(frame_lista_pecas, text="Atualizar Lista de Peças", command=self.atualizar_lista_pecas).pack(pady=5)

        # Frame inferior: Pendências por Usuário
        frame_pendencias = ttk.LabelFrame(parent, text="Pendências de Peças por Usuário", padding=10)
        frame_pendencias.pack(fill='both', expand=True, padx=10, pady=5)

        ttk.Label(frame_pendencias, text="Selecione Usuário:").pack(anchor='w', padx=5, pady=5)
        self.combo_usuario_pendencias = ttk.Combobox(frame_pendencias, width=20)
        self.combo_usuario_pendencias.pack(anchor='w', padx=5, pady=5)
        self.combo_usuario_pendencias.bind('<<ComboboxSelected>>', self.atualizar_pendencias_usuario)

        ttk.Button(frame_pendencias, text="Atualizar Pendências", command=self.atualizar_pendencias_usuario).pack(pady=5)

        columns_pend = ('Peça', 'Qtd Retirada', 'Qtd Devolvida', 'Pendente', 'Data Retirada', 'Status')
        self.tree_pendencias = ttk.Treeview(frame_pendencias, columns=columns_pend, show='headings', height=8)

        for col in columns_pend:
            self.tree_pendencias.heading(col, text=col)
            self.tree_pendencias.column(col, width=120)

        scrollbar_pend = ttk.Scrollbar(frame_pendencias, orient='vertical', command=self.tree_pendencias.yview)
        self.tree_pendencias.configure(yscrollcommand=scrollbar_pend.set)

        self.tree_pendencias.pack(side='left', fill='both', expand=True, pady=5)
        scrollbar_pend.pack(side='right', fill='y')

        # Inicializar dados da aba
        self.atualizar_lista_pecas()
        self.atualizar_combo_usuarios_pendencias()
        self.atualizar_pendencias_usuario()

    def atualizar_combo_usuarios_pendencias(self):
        usuarios = self.carrinho.db.listar_usuarios()
        self.combo_usuario_pendencias['values'] = [u.nome for u in usuarios]
        if usuarios:
            self.combo_usuario_pendencias.set(usuarios[0].nome)

    def cadastrar_peca(self):
        nome = self.entry_peca_nome.get().strip()
        desc = self.entry_peca_desc.get().strip()
        try:
            gaveta_id = int(self.entry_peca_gaveta.get().strip())
            qtd = int(self.entry_peca_qtd.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "Gaveta ID e Quantidade devem ser números inteiros válidos!")
            return

        if not nome or not desc or not (1 <= gaveta_id <= 5) or qtd < 0:
            messagebox.showerror("Erro", "Preencha todos os campos corretamente (Gaveta 1-5, Qtd >=0)!")
            return

        peca = Peca(
            id=0,  
            nome=nome,
            descricao=desc,
            gaveta_id=gaveta_id,
            quantidade_disponivel=qtd,
            ativo=True
        )

        if self.carrinho.adicionar_peca(peca):
            messagebox.showinfo("Sucesso", f"Peça '{nome}' cadastrada/atualizada na Gaveta {gaveta_id}!")
           
            self.entry_peca_nome.delete(0, tk.END)
            self.entry_peca_desc.delete(0, tk.END)
            self.entry_peca_gaveta.delete(0, tk.END)
            self.entry_peca_qtd.delete(0, tk.END)
            self.atualizar_lista_pecas()
        else:
            messagebox.showerror("Erro", "Falha ao cadastrar peça. Verifique os logs.")

    def atualizar_lista_pecas(self):
        for item in self.tree_pecas.get_children():
            self.tree_pecas.delete(item)
        pecas = self.carrinho.listar_todas_pecas()
        for peca in pecas:
            desc_short = peca.descricao[:30] + '...' if len(peca.descricao) > 30 else peca.descricao
            self.tree_pecas.insert('', 'end', values=(
                peca.id, peca.nome, desc_short, peca.gaveta_id, peca.quantidade_disponivel
            ))

    def atualizar_pendencias_usuario(self, event=None):
        nome_usuario = self.combo_usuario_pendencias.get()
        if not nome_usuario:
            return
        usuarios = self.carrinho.db.listar_usuarios()
        usuario = next((u for u in usuarios if u.nome == nome_usuario), None)
        if not usuario:
            return

        for item in self.tree_pendencias.get_children():
            self.tree_pendencias.delete(item)

        retiradas = self.carrinho.obter_pecas_pendentes_usuario(usuario.id)
        for ret in retiradas:
            peca = self.carrinho.db.obter_peca_por_id(ret.peca_id)
            nome_peca = peca.nome if peca else f"Peça ID {ret.peca_id}"
            pendente = ret.quantidade_retirada - ret.quantidade_devolvida
            try:
                data_ret = datetime.datetime.fromisoformat(ret.timestamp_retirada).strftime("%d/%m/%Y %H:%M")
            except:
                data_ret = ret.timestamp_retirada
            self.tree_pendencias.insert('', 'end', values=(
                nome_peca, ret.quantidade_retirada, ret.quantidade_devolvida, pendente, data_ret, ret.status
            ))

    # Integração com gavetas: Toggle com pop-ups de peças
    def toggle_gaveta_com_pecas(self, gaveta_id):
        if not self.usuario_atual:
            messagebox.showerror("Erro", "Valide um cartão autorizado primeiro!")
            return

        gaveta = self.carrinho.gavetas[gaveta_id]
        sucesso = False

        if not gaveta.aberta:
            # Abrir gaveta + pop-up retirada (opcional)
            sucesso = self.carrinho.abrir_gaveta(gaveta_id, self.usuario_atual.id)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Gaveta {gaveta_id} aberta!")
                # Pop-up para registrar retiradas
                self.mostrar_pop_up_retirada(gaveta_id)
            else:
                messagebox.showerror("Erro", f"Falha ao abrir Gaveta {gaveta_id}")
        else:
            # Pop-up devolução (opcional) + fechar gaveta
            self.mostrar_pop_up_devolucao(gaveta_id)
            sucesso = self.carrinho.fechar_gaveta(gaveta_id, self.usuario_atual.id)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Gaveta {gaveta_id} fechada!")
            else:
                messagebox.showerror("Erro", f"Falha ao fechar Gaveta {gaveta_id}")

        self.atualizar_status_gavetas()

    def mostrar_pop_up_retirada(self, gaveta_id):
        # Janela modal para retirada
        popup = tk.Toplevel(self.root)
        popup.title(f"Registrar Retirada - Gaveta {gaveta_id}")
        popup.geometry("400x300")
        popup.transient(self.root)
        popup.grab_set()  

        ttk.Label(popup, text=f"Peças disponíveis na Gaveta {gaveta_id}:").pack(pady=10)

        pecas = self.carrinho.listar_pecas_por_gaveta(gaveta_id)
        if not pecas:
            ttk.Label(popup, text="Nenhuma peça cadastrada nesta gaveta.").pack(pady=10)
            ttk.Button(popup, text="Fechar", command=popup.destroy).pack(pady=10)
            return

        valores_pecas = [f"{p.nome} (ID:{p.id}, Estoque:{p.quantidade_disponivel})" for p in pecas]
        self.combo_retirada_peca = ttk.Combobox(popup, values=valores_pecas, width=40)
        self.combo_retirada_peca.pack(pady=5)

        ttk.Label(popup, text="Quantidade a Retirar:").pack(pady=5)
        self.entry_retirada_qtd = ttk.Entry(popup, width=10)
        self.entry_retirada_qtd.pack(pady=5)

        def registrar_uma_retirada():
            if not self.combo_retirada_peca.get() or not self.entry_retirada_qtd.get():
                messagebox.showerror("Erro", "Selecione peça e quantidade!")
                return
            try:
                selected = self.combo_retirada_peca.get()
                peca_id = int(selected.split("(ID:")[1].split(")")[0])
                qtd = int(self.entry_retirada_qtd.get())
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida!")
                return

            if qtd <= 0:
                messagebox.showerror("Erro", "Quantidade deve ser >0!")
                return

            peca = self.carrinho.db.obter_peca_por_id(peca_id)
            if peca and peca.quantidade_disponivel < qtd:
                messagebox.showerror("Erro", f"Estoque insuficiente! Disponível: {peca.quantidade_disponivel}")
                return

            if self.carrinho.registrar_retirada_peca(self.usuario_atual.id, peca_id, qtd):
                messagebox.showinfo("Sucesso", f"{qtd} unidades de {peca.nome if peca else 'Peça'} retiradas!")
                # Limpar para próxima
                self.entry_retirada_qtd.delete(0, tk.END)
                self.combo_retirada_peca.set('')
                # Atualizar listas
                self.atualizar_lista_pecas()
                self.atualizar_pendencias_usuario()
            else:
                messagebox.showerror("Erro", "Falha ao registrar retirada. Verifique logs.")

        ttk.Button(popup, text="Registrar Retirada", command=registrar_uma_retirada).pack(pady=5)
        ttk.Button(popup, text="Adicionar Mais (Loop)", command=lambda: [registrar_uma_retirada(), popup.lift()]).pack(pady=2)  
        ttk.Button(popup, text="Cancelar (Apenas Abrir Gaveta)", command=popup.destroy).pack(pady=5)

    def mostrar_pop_up_devolucao(self, gaveta_id):
        # Janela modal para devolução
        popup = tk.Toplevel(self.root)
        popup.title(f"Registrar Devolução - Gaveta {gaveta_id}")
        popup.geometry("450x350")
        popup.transient(self.root)
        popup.grab_set()

        ttk.Label(popup, text=f"Retiradas pendentes do usuário na Gaveta {gaveta_id}:").pack(pady=10)

        # Buscar retiradas pendentes para esta gaveta e usuário
        conn = sqlite3.connect(self.carrinho.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, r.quantidade_retirada, r.quantidade_devolvida, p.nome
            FROM retiradas_pecas r JOIN pecas p ON r.peca_id = p.id
            WHERE r.usuario_id = ? AND p.gaveta_id = ? AND r.status IN ('pendente', 'parcial')
        ''', (self.usuario_atual.id, gaveta_id))
        retiradas = cursor.fetchall()
        conn.close()

        if not retiradas:
            ttk.Label(popup, text="Nenhuma retirada pendente nesta gaveta.").pack(pady=10)
            ttk.Button(popup, text="Fechar", command=popup.destroy).pack(pady=10)
            return

        valores_retiradas = [f"{row[3]} - ID Retirada:{row[0]}, Pendente:{row[1]-row[2]}" for row in retiradas]
        self.combo_devolucao_ret = ttk.Combobox(popup, values=valores_retiradas, width=45)
        self.combo_devolucao_ret.pack(pady=5)

        ttk.Label(popup, text="Quantidade a Devolver (0 para pular):").pack(pady=5)
        self.entry_devolucao_qtd = ttk.Entry(popup, width=10)
        self.entry_devolucao_qtd.pack(pady=5)

        def registrar_uma_devolucao():
            if not self.combo_devolucao_ret.get() or not self.entry_devolucao_qtd.get().strip():
                messagebox.showerror("Erro", "Selecione retirada e quantidade!")
                return
            try:
                selected = self.combo_devolucao_ret.get()
                retirada_id = int(selected.split("ID Retirada:")[1].split(",")[0])
                qtd = int(self.entry_devolucao_qtd.get())
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida!")
                return

            if qtd < 0:
                messagebox.showerror("Erro", "Quantidade deve ser >=0!")
                return

            # Verificar pendente
            conn = sqlite3.connect(self.carrinho.db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT quantidade_retirada - quantidade_devolvida FROM retiradas_pecas WHERE id = ?', (retirada_id,))
            pendente = cursor.fetchone()[0] if cursor.fetchone() else None
            if pendente and qtd > pendente[0]:
                messagebox.showerror("Erro", f"Não pode devolver mais que pendente ({pendente[0]} unidades)!")
                conn.close()
                return

            if qtd > 0 and self.carrinho.registrar_devolucao_peca(retirada_id, qtd):
                messagebox.showinfo("Sucesso", f"{qtd} unidades devolvidas para a retirada {retirada_id}!")
                self.entry_devolucao_qtd.delete(0, tk.END)
                self.combo_devolucao_ret.set('')
                self.atualizar_lista_pecas()
                self.atualizar_pendencias_usuario()
            elif qtd == 0:
                messagebox.showinfo("Info", "Devolução pulada (qtd=0).")
            else:
                messagebox.showerror("Erro", "Falha ao registrar devolução. Verifique logs.")
            conn.close()

        ttk.Button(popup, text="Registrar Devolução", command=registrar_uma_devolucao).pack(pady=5)
        ttk.Button(popup, text="Adicionar Mais Devoluções", command=lambda: [registrar_uma_devolucao(), popup.lift()]).pack(pady=2)
        ttk.Button(popup, text="Cancelar (Apenas Fechar Gaveta)", command=popup.destroy).pack(pady=5)

    def processar_cartao(self, event=None):
        codigo_cartao = self.entry_cartao.get().strip()
        if not codigo_cartao:
            return

        usuario = self.carrinho.validar_cartao(codigo_cartao)
        if usuario:
            self.label_usuario_atual.config(
                text=f"Usuário: {usuario.nome} ({usuario.cargo})",
                foreground='green'
            )
            self.usuario_atual = usuario
        else:
            self.label_usuario_atual.config(
                text="Cartão não autorizado!",
                foreground='red'
            )
            self.usuario_atual = None

        self.entry_cartao.delete(0, tk.END)
        self.root.after(0, self.atualizar_combo_usuarios_pendencias)

    def cadastrar_usuario(self):
        id_cartao = self.entry_novo_id.get().strip()
        nome = self.entry_novo_nome.get().strip()
        cargo = self.combo_cargo.get().strip()

        if not all([id_cartao, nome, cargo]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        usuario = UsuarioCartao(
            id=id_cartao,
            nome=nome,
            cargo=cargo,
            ativo=True,
            data_cadastro=datetime.datetime.now().isoformat()
        )

        try:
            self.carrinho.db.adicionar_usuario(usuario)
            messagebox.showinfo("Sucesso", f"Usuário {nome} cadastrado com sucesso!")
            self.entry_novo_id.delete(0, tk.END)
            self.entry_novo_nome.delete(0, tk.END)
            self.combo_cargo.set('')
            self.atualizar_lista_usuarios()
            self.atualizar_combo_usuarios_pendencias()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}")

    def atualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)

        usuarios = self.carrinho.db.listar_usuarios()
        for usuario in usuarios:
            try:
                data_cadastro = datetime.datetime.fromisoformat(usuario.data_cadastro).strftime("%d/%m/%Y %H:%M")
            except Exception:
                data_cadastro = usuario.data_cadastro or "N/A"
            self.tree_usuarios.insert('', 'end', values=(
                usuario.id, usuario.nome, usuario.cargo, data_cadastro
            ))

    def remover_usuario_selecionado(self):
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um usuário para remover!")
            return

        item = selection[0]
        usuario_id = self.tree_usuarios.item(item)['values'][0]
        nome_usuario = self.tree_usuarios.item(item)['values'][1]

        if messagebox.askyesno("Confirmar", f"Deseja realmente remover o usuário {nome_usuario}?"):
            try:
                conn = sqlite3.connect(self.carrinho.db.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE usuarios SET ativo = 0 WHERE id = ?', (usuario_id,))
                conn.commit()
                conn.close()

                messagebox.showinfo("Sucesso", f"Usuário {nome_usuario} removido!")
                self.atualizar_lista_usuarios()
                self.atualizar_combo_usuarios_pendencias()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover usuário: {e}")

    def atualizar_historico(self):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)

        eventos = self.carrinho.db.obter_historico(100)
        for evento in eventos:
            try:
                timestamp = datetime.datetime.fromisoformat(evento.timestamp).strftime("%d/%m/%Y %H:%M:%S")
            except Exception:
                timestamp = evento.timestamp
            status = "✓ Sucesso" if evento.sucesso else "✗ Falha"

            usuario = self.carrinho.db.obter_usuario(evento.usuario_id)
            nome_usuario = usuario.nome if usuario else evento.usuario_id

            self.tree_historico.insert('', 'end', values=(
                timestamp, f"Gaveta {evento.gaveta_id}", nome_usuario,
                evento.acao.capitalize(), status
            ))

    def atualizar_status_gavetas(self):
        for gaveta_id, gaveta in self.carrinho.gavetas.items():
            label = self.labels_status_gavetas[gaveta_id]
            botao = self.botoes_gavetas[gaveta_id]
            info_label = self.info_labels_gavetas[gaveta_id]

            if gaveta.aberta:
                label.config(text="ABERTA", foreground='red')
                botao.config(text="Fechar")

                tempo_aberta = gaveta.tempo_aberta()
                texto_tempo = f" ({tempo_aberta//60}min)" if tempo_aberta > 60 else ""
                label.config(text=f"ABERTA{texto_tempo}", foreground='orange' if tempo_aberta < 600 else 'red')

                conn = sqlite3.connect(self.carrinho.db.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM retiradas_pecas r JOIN pecas p ON r.peca_id = p.id
                    WHERE p.gaveta_id = ? AND r.status IN ('pendente', 'parcial')
                ''', (gaveta_id,))
                num_pendentes = cursor.fetchone()[0]
                conn.close()
                info_label.config(text=f"{num_pendentes} itens pendentes" if num_pendentes > 0 else "--")
            else:
                label.config(text="FECHADA", foreground='green')
                botao.config(text="Abrir")
                info_label.config(text="--")

    def atualizar_status_periodico(self):
        self.atualizar_status_gavetas()
        self.atualizar_alertas()
        self.atualizar_historico()
        self.root.after(10000, self.atualizar_lista_pecas)
        self.root.after(10000, self.atualizar_pendencias_usuario)
        self.root.after(2000, self.atualizar_status_periodico)

    def atualizar_alertas(self):
        alertas_texto = ""
        for alerta in self.carrinho.alertas_ativos:
            try:
                timestamp = datetime.datetime.fromisoformat(alerta['timestamp']).strftime("%H:%M:%S")
            except Exception:
                timestamp = alerta['timestamp']
            mensagem = alerta['mensagem']
            alertas_texto += f"[{timestamp}] {mensagem}\n"

            if mensagem not in self.alertas_exibidos:
                self.alertas_exibidos.add(mensagem)
                self.root.after(0, lambda msg=mensagem: messagebox.showwarning("Alerta de Gaveta", msg))

        self.text_alertas.delete(1.0, tk.END)
        self.text_alertas.insert(1.0, alertas_texto)
        self.text_alertas.see(tk.END)

    def fechar_todas_gavetas(self):
        if messagebox.askyesno("Confirmar", "Deseja fechar todas as gavetas abertas?"):
            gavetas_fechadas = 0
            for gaveta_id, gaveta in self.carrinho.gavetas.items():
                if gaveta.aberta:
                    if self.carrinho.fechar_gaveta(gaveta_id):
                        gavetas_fechadas += 1
            messagebox.showinfo("Sucesso", f"{gavetas_fechadas} gaveta(s) fechada(s)!")
            self.atualizar_status_gavetas()
            # Atualiza pendências após fechamentos em massa
            self.atualizar_pendencias_usuario()

    def limpar_alertas(self):
        self.carrinho.alertas_ativos.clear()
        self.text_alertas.delete(1.0, tk.END)
        self.alertas_exibidos.clear()
        messagebox.showinfo("Sucesso", "Alertas limpos!")

    def exportar_logs(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo_txt = f"relatorio_carrinho_{timestamp}.txt"
            nome_arquivo_json = f"relatorio_carrinho_{timestamp}.json"

            usuarios = self.carrinho.db.listar_usuarios()
            eventos = self.carrinho.db.obter_historico(50)
            pecas = self.carrinho.listar_todas_pecas()

            # Buscar pendências ativas (todas)
            conn = sqlite3.connect(self.carrinho.db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, p.nome FROM retiradas_pecas r JOIN pecas p ON r.peca_id = p.id
                WHERE r.status IN ('pendente', 'parcial') ORDER BY r.timestamp_retirada DESC
            ''')
            pendencias_raw = cursor.fetchall()
            conn.close()

            pendencias = []
            for row in pendencias_raw:
                pend = row[3] - row[4]  
                pendencias.append({
                    'retirada_id': row[0], 'usuario_id': row[1], 'peca_nome': row[8],
                    'qtd_retirada': row[3], 'qtd_devolvida': row[4], 'pendente': pend,
                    'timestamp_retirada': row[5], 'status': row[7]
                })

            with open(nome_arquivo_txt, 'w', encoding='utf-8') as f:
                f.write("=== RELATÓRIO DO SISTEMA CARRINHO INTELIGENTE ===\n\n")
                f.write(f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

                f.write("STATUS DAS GAVETAS:\n")
                for gaveta_id, gaveta in self.carrinho.gavetas.items():
                    status = "ABERTA" if gaveta.aberta else "FECHADA"
                    tempo = f" (aberta há {gaveta.tempo_aberta()}s)" if gaveta.aberta else ""
                    f.write(f"- Gaveta {gaveta_id}: {status}{tempo}\n")
                f.write("\n")

                f.write("USUÁRIOS CADASTRADOS:\n")
                for usuario in usuarios:
                    try:
                        data_cadastro = datetime.datetime.fromisoformat(usuario.data_cadastro).strftime("%d/%m/%Y %H:%M")
                    except:
                        data_cadastro = "N/A"
                    f.write(f"- {usuario.nome} ({usuario.cargo}) - ID: {usuario.id} - Cadastrado: {data_cadastro}\n")
                f.write("\n")

                f.write("INVENTÁRIO DE PEÇAS:\n")
                for peca in pecas:
                    f.write(f"- {peca.nome} (Gaveta {peca.gaveta_id}): {peca.quantidade_disponivel} disponíveis\n")
                f.write("\n")

                f.write("ALERTAS ATIVOS:\n")
                for alerta in self.carrinho.alertas_ativos:
                    try:
                        ts = datetime.datetime.fromisoformat(alerta['timestamp']).strftime("%d/%m/%Y %H:%M:%S")
                    except:
                        ts = alerta['timestamp']
                    f.write(f"- {ts}: {alerta['mensagem']}\n")
                f.write("\n")

                f.write("PENDÊNCIAS ATIVAS (Peças Não Devolvidas):\n")
                if pendencias:
                    for p in pendencias:
                        try:
                            data_ret = datetime.datetime.fromisoformat(p['timestamp_retirada']).strftime("%d/%m/%Y %H:%M")
                        except:
                            data_ret = p['timestamp_retirada']
                        usuario = next((u for u in usuarios if u.id == p['usuario_id']), None)
                        nome_usu = usuario.nome if usuario else p['usuario_id']
                        f.write(f"- {nome_usu}: {p['peca_nome']} - {p['pendente']} pendentes (retirados {p['qtd_retirada']}, devolvidos {p['qtd_devolvida']}) em {data_ret}\n")
                else:
                    f.write("- Nenhuma pendência ativa.\n")
                f.write("\n")

                f.write("HISTÓRIO RECENTE (últimos 50 eventos):\n")
                for evento in eventos:
                    try:
                        timestamp_evento = datetime.datetime.fromisoformat(evento.timestamp).strftime("%d/%m/%Y %H:%M:%S")
                    except Exception:
                        timestamp_evento = evento.timestamp
                    status = "SUCESSO" if evento.sucesso else "FALHA"
                    usuario = self.carrinho.db.obter_usuario(evento.usuario_id)
                    nome_usuario = usuario.nome if usuario else evento.usuario_id
                    f.write(f"- {timestamp_evento} | Gaveta {evento.gaveta_id} | {nome_usuario} | {evento.acao.upper()} | {status}\n")

            relatorio_json = {
                "gerado_em": datetime.datetime.now().isoformat(),
                "status_gavetas": {str(g.id): {"aberta": g.aberta, "tempo_aberta": g.tempo_aberta()} for g in self.carrinho.gavetas.values()},
                "usuarios": [{"id": u.id, "nome": u.nome, "cargo": u.cargo, "data_cadastro": u.data_cadastro} for u in usuarios],
                "pecas": [{"id": p.id, "nome": p.nome, "descricao": p.descricao, "gaveta_id": p.gaveta_id, "quantidade_disponivel": p.quantidade_disponivel} for p in pecas],
                "alertas_ativos": [{"timestamp": a['timestamp'], "mensagem": a['mensagem']} for a in self.carrinho.alertas_ativos],
                "pendencias_ativas": pendencias,  
                "historico_recente": [
                    {
                        "timestamp": evento.timestamp,
                        "gaveta_id": evento.gaveta_id,
                        "usuario_id": evento.usuario_id,
                        "acao": evento.acao,
                        "sucesso": evento.sucesso
                    } for evento in eventos
                ]
            }

            with open(nome_arquivo_json, 'w', encoding='utf-8') as f:
                json.dump(relatorio_json, f, indent=4, ensure_ascii=False)

            messagebox.showinfo(
                "Relatório Exportado",
                f"Relatórios gerados com sucesso!\n\n"
                f"- TXT: {nome_arquivo_txt}\n"
                f"- JSON: {nome_arquivo_json}\n\n"
                f"Local: {os.getcwd()}\n\n"
                f"Pendências ativas: {len(pendencias)} itens não devolvidos."
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar logs: {e}")
            logging.error(f"Erro no exportar_logs: {e}")

    def executar(self):
        """Inicia a interface gráfica."""
        self.root.mainloop()

    def _on_close(self):
        """Manipula o fechamento da janela."""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?\nTodas as gavetas abertas serão fechadas."):
            for gaveta_id in self.carrinho.gavetas:
                if self.carrinho.gavetas[gaveta_id].aberta:
                    self.carrinho.fechar_gaveta(gaveta_id)
            self.carrinho.sistema_ativo = False
            # Limpar alertas
            self.carrinho.alertas_ativos.clear()
            # Destruir janela
            self.root.destroy()
            logging.info("Sistema encerrado pelo usuário.")