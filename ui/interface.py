import datetime
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


from core.cart import CarrinhoInteligenteAvancado
from models.entities import Peca, UsuarioCartao
from ui.painelMonitoramento import PainelMonitoramento


class InterfaceGraficaCarrinho:

    def abrir_painel_monitoramento(self):
      if not hasattr(self, 'painel_monitoramento') or not self.painel_monitoramento.root.winfo_exists():
         self.painel_monitoramento = PainelMonitoramento(self.carrinho)
      else:
        self.painel_monitoramento.root.lift()
    def __init__(self, carrinho: 'CarrinhoInteligenteAvancado' = None):
        if carrinho:
            self.carrinho = carrinho
        else:
            self.carrinho = CarrinhoInteligenteAvancado()
        self.root = tk.Tk()
        self.root.title("Controle de Retirada e Devolução de Ferramentas")
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
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)


        # Aba Principal (atualizada para busca e retirada)
        frame_principal = ttk.Frame(self.notebook)
        self.notebook.add(frame_principal, text="Painel de Retirada")
        self.setup_aba_principal(frame_principal)


        # Aba de Usuários (admin)
        frame_usuarios = ttk.Frame(self.notebook)
        self.notebook.add(frame_usuarios, text="Gerenciar Usuários")
        self.setup_aba_usuarios(frame_usuarios)


        # Aba de Histórico (admin)
        frame_historico = ttk.Frame(self.notebook)
        self.notebook.add(frame_historico, text="Histórico")
        self.setup_aba_historico(frame_historico)


        # Aba Inventário e Pendências (admin)
        frame_inventario = ttk.Frame(self.notebook)
        self.notebook.add(frame_inventario, text="Inventário e Pendências")
        self.setup_aba_inventario(frame_inventario)


    def setup_aba_principal(self, parent):
        frame_cartao = ttk.LabelFrame(parent, text="Acesso por Cartão / RFID", padding=10)
        frame_cartao.pack(fill='x', padx=10, pady=5)


        ttk.Label(frame_cartao, text="Código do Cartão:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_cartao = ttk.Entry(frame_cartao, font=('Arial', 12), width=20)
        self.entry_cartao.grid(row=0, column=1, padx=5, pady=5)
        self.entry_cartao.bind('<Return>', self.processar_cartao)


        ttk.Button(frame_cartao, text="Validar Cartão", command=self.processar_cartao).grid(row=0, column=2, padx=5)


        ttk.Button(frame_cartao, text="Ler RFID", command=self.ler_rfid).grid(row=0, column=3, padx=5)


        self.label_usuario_atual = ttk.Label(frame_cartao, text="Nenhum usuário identificado", foreground='red')
        self.label_usuario_atual.grid(row=1, column=0, columnspan=4, pady=5)


        frame_busca = ttk.LabelFrame(parent, text="Buscar Peça para Retirada", padding=10)
        frame_busca.pack(fill='x', padx=10, pady=5)


        ttk.Label(frame_busca, text="Nome da Peça:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_peca = ttk.Entry(frame_busca, width=40)
        self.entry_busca_peca.grid(row=0, column=1, padx=5, pady=5)
        self.entry_busca_peca.bind('<Return>', self.buscar_e_abrir_gaveta)


        ttk.Button(frame_busca, text="Buscar e Abrir Gaveta", command=self.buscar_e_abrir_gaveta).grid(row=0, column=2, padx=5)


        # Status gavetas
        frame_status = ttk.LabelFrame(parent, text="Status das Gavetas", padding=10)
        frame_status.pack(fill='both', expand=True, padx=10, pady=5)


        self.labels_status_gavetas = {}
        for i in range(1, 6):
            lbl = ttk.Label(frame_status, text=f"Gaveta {i}: FECHADA", foreground='green', font=('Arial', 10, 'bold'))
            lbl.pack(anchor='w', pady=2)
            self.labels_status_gavetas[i] = lbl


    def ler_rfid(self):
        codigo = self.carrinho.hardware.ler_rfid()
        if codigo:
            self.entry_cartao.delete(0, tk.END)
            self.entry_cartao.insert(0, codigo)
            self.processar_cartao()
        else:
            messagebox.showinfo("RFID", "Nenhum RFID detectado (simulação).")


    def processar_cartao(self, event=None):
        codigo_cartao = self.entry_cartao.get().strip()
        if not codigo_cartao:
            return


        usuario = self.carrinho.validar_cartao(codigo_cartao)
        if usuario:
            self.label_usuario_atual.config(
                text=f"Usuário: {usuario.nome} ({usuario.cargo}) - Perfil: {usuario.perfil}",
                foreground='green'
            )
            self.usuario_atual = usuario
            self.configurar_acesso_por_perfil(usuario.perfil)
        else:
            self.label_usuario_atual.config(
                text="Cartão não autorizado!",
                foreground='red'
            )
            self.usuario_atual = None
            self.configurar_acesso_por_perfil(None)


        self.entry_cartao.delete(0, tk.END)


    def configurar_acesso_por_perfil(self, perfil):
        if perfil == "admin":
            for i in range(len(self.notebook.tabs())):
                self.notebook.tab(i, state='normal')
        elif perfil == "aluno":
            for i in range(len(self.notebook.tabs())):
                state = 'normal' if i == 0 else 'hidden'
                self.notebook.tab(i, state=state)
        else:
            for i in range(len(self.notebook.tabs())):
                self.notebook.tab(i, state='hidden')


    def buscar_e_abrir_gaveta(self, event=None):
        if not self.usuario_atual:
            messagebox.showerror("Erro", "Valide um cartão autorizado primeiro!")
            return


        nome_peca = self.entry_busca_peca.get().strip()
        if not nome_peca:
            messagebox.showerror("Erro", "Digite o nome da peça para buscar!")
            return


        pecas = self.carrinho.db.listar_todas_pecas()
        peca_encontrada = None
        for p in pecas:
            if nome_peca.lower() in p.nome.lower():
                peca_encontrada = p
                break


        if not peca_encontrada:
            messagebox.showerror("Erro", f"Peça '{nome_peca}' não encontrada no inventário.")
            return


        gaveta_id = peca_encontrada.gaveta_id
        sucesso = self.carrinho.abrir_gaveta(gaveta_id, self.usuario_atual.id)
        if sucesso:
            messagebox.showinfo("Sucesso", f"Gaveta {gaveta_id} aberta para a peça '{peca_encontrada.nome}'.")
            self.mostrar_pop_up_retirada(gaveta_id)
            self.atualizar_status_gavetas()
        else:
            messagebox.showerror("Erro", f"Falha ao abrir Gaveta {gaveta_id}.")


        self.entry_busca_peca.delete(0, tk.END)
        #alteração
        def setup_interface(self):
          self.notebook = ttk.Notebook(self.root)
          self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.btn_monitoramento = ttk.Button(self.root, text="Abrir Painel de Monitoramento", command=self.abrir_painel_monitoramento)
        self.btn_monitoramento.pack(pady=5)
        self.btn_monitoramento.pack_forget()  


    def mostrar_pop_up_retirada(self, gaveta_id):
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
        combo_retirada_peca = ttk.Combobox(popup, values=valores_pecas, width=40)
        combo_retirada_peca.pack(pady=5)


        ttk.Label(popup, text="Quantidade a Retirar:").pack(pady=5)
        entry_retirada_qtd = ttk.Entry(popup, width=10)
        entry_retirada_qtd.pack(pady=5)


        def registrar_uma_retirada():
            if not combo_retirada_peca.get() or not entry_retirada_qtd.get():
                messagebox.showerror("Erro", "Selecione peça e quantidade!")
                return
            try:
                selected = combo_retirada_peca.get()
                peca_id = int(selected.split("(ID:")[1].split(")")[0])
                qtd = int(entry_retirada_qtd.get())
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
                entry_retirada_qtd.delete(0, tk.END)
                combo_retirada_peca.set('')
                self.atualizar_status_gavetas()
            else:
                messagebox.showerror("Erro", "Falha ao registrar retirada. Verifique logs.")


        ttk.Button(popup, text="Registrar Retirada", command=registrar_uma_retirada).pack(pady=5)
        ttk.Button(popup, text="Cancelar", command=popup.destroy).pack(pady=5)


    def atualizar_status_gavetas(self):
        for gaveta_id, gaveta in self.carrinho.gavetas.items():
            label = self.labels_status_gavetas[gaveta_id]
            if gaveta.aberta:
                tempo_aberta = gaveta.tempo_aberta()
                texto_tempo = f" (aberta há {tempo_aberta//60} min {tempo_aberta%60} s)" if tempo_aberta > 0 else ""
                label.config(text=f"Gaveta {gaveta_id}: ABERTA{texto_tempo}", foreground='red')
            else:
                label.config(text=f"Gaveta {gaveta_id}: FECHADA", foreground='green')


    def atualizar_status_periodico(self):
        # Atualiza o status das gavetas a cada 5 segundos
        self.atualizar_status_gavetas()
        self.root.after(5000, self.atualizar_status_periodico)


    def executar(self):
        self.root.mainloop()


    def _on_close(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?\nTodas as gavetas abertas serão fechadas."):
            for gaveta_id in self.carrinho.gavetas:
                if self.carrinho.gavetas[gaveta_id].aberta:
                    self.carrinho.fechar_gaveta(gaveta_id)
            self.carrinho.sistema_ativo = False
            self.carrinho.alertas_ativos.clear()
            self.root.destroy()
            logging.info("Sistema encerrado pelo usuário.")


    # --- Aba Usuários ---


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
        self.entry_novo_cargo = ttk.Entry(frame_add, width=20)
        self.entry_novo_cargo.grid(row=1, column=1, padx=5, pady=5)


        ttk.Label(frame_add, text="Perfil:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.combo_perfil = ttk.Combobox(frame_add, values=["admin", "aluno"], width=18)
        self.combo_perfil.grid(row=1, column=3, padx=5, pady=5)


        ttk.Button(frame_add, text="Cadastrar Usuário", command=self.cadastrar_usuario).grid(row=2, column=0, columnspan=4, pady=10)


        frame_lista = ttk.LabelFrame(parent, text="Usuários Cadastrados", padding=10)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)


        columns = ('ID', 'Nome', 'Cargo', 'Perfil', 'Data Cadastro')
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


    def cadastrar_usuario(self):
        id_cartao = self.entry_novo_id.get().strip()
        nome = self.entry_novo_nome.get().strip()
        cargo = self.entry_novo_cargo.get().strip()
        perfil = self.combo_perfil.get().strip()


        if not all([id_cartao, nome, cargo, perfil]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return


        usuario = UsuarioCartao(
            id=id_cartao,
            nome=nome,
            cargo=cargo,
            perfil=perfil,
            ativo=True,
            data_cadastro=datetime.datetime.now().isoformat()
        )


        try:
            self.carrinho.db.adicionar_usuario(usuario)
            messagebox.showinfo("Sucesso", f"Usuário {nome} cadastrado com sucesso!")
            self.entry_novo_id.delete(0, tk.END)
            self.entry_novo_nome.delete(0, tk.END)
            self.entry_novo_cargo.delete(0, tk.END)
            self.combo_perfil.set('')
            self.atualizar_lista_usuarios()
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
                usuario.id, usuario.nome, usuario.cargo, usuario.perfil, data_cadastro
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
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover usuário: {e}")


    # --- Aba Histórico ---


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


    # --- Aba Inventário e Pendências ---


    def setup_aba_inventario(self, parent):
        frame_gerenciar = ttk.LabelFrame(parent, text="Gerenciar Peças (Inventário)", padding=10)
        frame_gerenciar.pack(fill='x', padx=10, pady=5)


        ttk.Label(frame_gerenciar, text="Nome:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_peca_nome = ttk.Entry(frame_gerenciar, width=20)
        self.entry_peca_nome.grid(row=0, column=1, padx=5, pady=5)


        ttk.Label(frame_gerenciar, text="Categoria:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.entry_peca_categoria = ttk.Entry(frame_gerenciar, width=20)
        self.entry_peca_categoria.grid(row=0, column=3, padx=5, pady=5)


        ttk.Label(frame_gerenciar, text="Descrição:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_peca_desc = ttk.Entry(frame_gerenciar, width=30)
        self.entry_peca_desc.grid(row=1, column=1, padx=5, pady=5)


        ttk.Label(frame_gerenciar, text="Tipo:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_peca_tipo = ttk.Entry(frame_gerenciar, width=20)
        self.entry_peca_tipo.grid(row=1, column=3, padx=5, pady=5)


        ttk.Label(frame_gerenciar, text="Gaveta ID (1-5):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_peca_gaveta = ttk.Entry(frame_gerenciar, width=10)
        self.entry_peca_gaveta.grid(row=2, column=1, padx=5, pady=5)


        ttk.Label(frame_gerenciar, text="Quantidade Disponível:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.entry_peca_qtd = ttk.Entry(frame_gerenciar, width=10)
        self.entry_peca_qtd.grid(row=2, column=3, padx=5, pady=5)


        ttk.Button(frame_gerenciar, text="Adicionar/Atualizar Peça", command=self.cadastrar_peca).grid(row=3, column=0, columnspan=4, pady=10)


        frame_lista_pecas = ttk.LabelFrame(parent, text="Todas as Peças", padding=10)
        frame_lista_pecas.pack(fill='both', expand=True, padx=10, pady=5)


        columns_pecas = ('ID', 'Nome', 'Categoria', 'Descrição', 'Tipo', 'Gaveta', 'Qtd Disponível')
        self.tree_pecas = ttk.Treeview(frame_lista_pecas, columns=columns_pecas, show='headings', height=10)


        for col in columns_pecas:
            self.tree_pecas.heading(col, text=col)
            self.tree_pecas.column(col, width=120)


        scrollbar_pecas = ttk.Scrollbar(frame_lista_pecas, orient='vertical', command=self.tree_pecas.yview)
        self.tree_pecas.configure(yscrollcommand=scrollbar_pecas.set)


        self.tree_pecas.pack(side='left', fill='both', expand=True)
        scrollbar_pecas.pack(side='right', fill='y')


        ttk.Button(frame_lista_pecas, text="Atualizar Lista de Peças", command=self.atualizar_lista_pecas).pack(pady=5)


        # Pendências por usuário
        frame_pendencias = ttk.LabelFrame(parent, text="Pendências de Peças por Usuário", padding=10)
        frame_pendencias.pack(fill='both', expand=True, padx=10, pady=5)


        ttk.Label(frame_pendencias, text="Selecione Usuário:").pack(anchor='w', padx=5, pady=5)
        self.combo_usuario_pendencias = ttk.Combobox(frame_pendencias, width=30)
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


        self.atualizar_lista_pecas()
        self.atualizar_combo_usuarios_pendencias()
        self.atualizar_pendencias_usuario()


    def cadastrar_peca(self):
        nome = self.entry_peca_nome.get().strip()
        categoria = self.entry_peca_categoria.get().strip()
        descricao = self.entry_peca_desc.get().strip()
        tipo = self.entry_peca_tipo.get().strip()
        try:
            gaveta_id = int(self.entry_peca_gaveta.get().strip())
            qtd = int(self.entry_peca_qtd.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "Gaveta ID e Quantidade devem ser números inteiros válidos!")
            return


        if not nome or not categoria or not tipo or not (1 <= gaveta_id <= 5) or qtd < 0:
            messagebox.showerror("Erro", "Preencha todos os campos corretamente (Gaveta 1-5, Qtd >=0)!")
            return


        peca = Peca(
            id=0,
            nome=nome,
            categoria=categoria,
            descricao=descricao,
            tipo=tipo,
            gaveta_id=gaveta_id,
            quantidade_disponivel=qtd,
            ativo=True
        )


        if self.carrinho.adicionar_peca(peca):
            messagebox.showinfo("Sucesso", f"Peça '{nome}' cadastrada/atualizada na Gaveta {gaveta_id}!")
            self.entry_peca_nome.delete(0, tk.END)
            self.entry_peca_categoria.delete(0, tk.END)
            self.entry_peca_desc.delete(0, tk.END)
            self.entry_peca_tipo.delete(0, tk.END)
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
                peca.id, peca.nome, peca.categoria, desc_short, peca.tipo, peca.gaveta_id, peca.quantidade_disponivel
            ))


    def atualizar_combo_usuarios_pendencias(self):
        usuarios = self.carrinho.db.listar_usuarios()
        self.combo_usuario_pendencias['values'] = [u.nome for u in usuarios]
        if usuarios:
            self.combo_usuario_pendencias.set(usuarios[0].nome)


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
            except Exception:
                data_ret = ret.timestamp_retirada
            self.tree_pendencias.insert('', 'end', values=(
                nome_peca, ret.quantidade_retirada, ret.quantidade_devolvida, pendente, data_ret, ret.status
            ))

    def abrir_painel_monitoramento(self):
        if not hasattr(self, 'painel_monitoramento') or not self.painel_monitoramento.root.winfo_exists():
          self.painel_monitoramento = PainelMonitoramento(self.carrinho)
        else:
          self.painel_monitoramento.root.lift()
 
   