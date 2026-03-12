import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import CORES, FONTES

class AbaPrincipal(ttk.Frame):
    
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent)
        self.carrinho = carrinho_controller
        self.app = app_controller  

        self.labels_status_gavetas = {}
        self.pecas_selecionadas = []
        
        self.setup_widgets()
        self.atualizar_status_gavetas()

    def setup_widgets(self):
        style = ttk.Style()
        # --- Configuração de Estilos ---
        style.configure("Verde.TButton", font=FONTES["botao"], background=CORES["sucesso"], foreground=CORES["texto_claro"])
        style.map('Verde.TButton', background=[('active', '#27ae60')])
        style.configure("Azul.TButton", font=FONTES["botao"], background=CORES["destaque"], foreground=CORES["texto_claro"])
        style.map('Azul.TButton', background=[('active', '#2980b9')])
        style.configure("Vermelho.TButton", font=FONTES["botao"], background=CORES["cancelar"], foreground=CORES["texto_claro"])
        style.map("Vermelho.TButton", background=[('active', '#c0392b')])
        style.configure("Alerta.TButton", font=FONTES["botao"], background=CORES["alerta"], foreground=CORES["texto_claro"])
        style.map("Alerta.TButton", background=[('active', '#e67e22')])

        # --- Frame de Acesso por RFID (agora ativado) ---
        #frame_rfid = ttk.LabelFrame(self, text="Acesso por RFID")
        #frame_rfid.pack(fill='x', padx=10, pady=10, ipady=10)

        #self.label_usuario_atual = ttk.Label(frame_rfid, text="Nenhum usuário identificado", foreground=CORES["alerta"], font=FONTES["corpo"])
        #self.label_usuario_atual.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

        #ttk.Button(frame_rfid, text="Ler RFID (Login)", command=self.ler_rfid).grid(row=0, column=2, padx=10, pady=10)

        frame_busca = ttk.LabelFrame(self, text="Buscar Chave para Retirada")
        frame_busca.pack(fill='x', padx=10, pady=10, ipady=10)
        
        self.frame_tags = tk.Frame(frame_busca)
        self.frame_tags.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky='w')

        ttk.Label(frame_busca, text="Nome da Chave:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.entry_busca_peca = ttk.Entry(frame_busca, width=40, font=FONTES["corpo"])
        self.entry_busca_peca.grid(row=1, column=1, padx=10, pady=10, ipady=5)
        
        self.listbox_sugestoes = tk.Listbox(frame_busca, height=5, font=FONTES["corpo"])
        self.listbox_sugestoes.grid(row=2, column=1, columnspan=2, padx=10, pady=(0, 10), sticky="we")
        self.listbox_sugestoes.grid_remove()
        
        self.entry_busca_peca.bind("<KeyRelease>", self._atualizar_sugestoes)
        self.listbox_sugestoes.bind("<<ListboxSelect>>", self._selecionar_sugestao)
        self.bind_all("<Button-1>", self._esconder_sugestoes_se_clicar_fora)

        botoes_frame = ttk.Frame(frame_busca)
        botoes_frame.grid(row=3, column=1, columnspan=2, pady=10, sticky='e')

        ttk.Button(botoes_frame, text="Abrir Gavetas e Registrar Retirada", command=self.abrir_gavetas_selecionadas, style="Verde.TButton").pack(side="left", padx=5)
        ttk.Button(botoes_frame, text="Limpar Seleção", command=self.limpar_selecao, style="Vermelho.TButton").pack(side="left", padx=5)

        # --- Frame de Ações do Usuário ---
        frame_acoes = ttk.LabelFrame(self, text="Ações do Usuário")
        frame_acoes.pack(fill='x', padx=10, pady=10, ipady=10)
        ttk.Button(frame_acoes, text="Devolver Chave", command=self.mostrar_popup_devolucao, style="Azul.TButton").pack(side="left", padx=10, pady=5)
        self.botao_abrir_todas = ttk.Button(frame_acoes, text="Abrir Todas as Gavetas (Admin)", command=self.abrir_todas_gavetas_admin, style="Alerta.TButton")
        # self.botao_abrir_todas.pack(side="left", padx=10) # Descomente se quiser o botão visível por padrão

        # --- Frame de Status das Gavetas ---
        frame_status = ttk.LabelFrame(self, text="Status das Gavetas")
        frame_status.pack(fill='both', expand=True, padx=10, pady=10)
        for i in range(1, 6):
            lbl = ttk.Label(frame_status, text=f"Gaveta {i}: FECHADA", foreground='green', font=FONTES["subtitulo"])
            lbl.pack(anchor='w', pady=5, padx=10)
            self.labels_status_gavetas[i] = lbl
        ttk.Button(frame_status, text="Fechar Gavetas Abertas", command=self.fechar_gavetas_abertas, style="Azul.TButton").pack(pady=10)

    def ler_rfid(self):
        try:
            # O 'or' é para teste, remova em produção se não precisar
            codigo = self.carrinho.hardware.ler_rfid() or "admin_card_001" 
            if codigo:
                self.processar_cartao(codigo)
            else:
                messagebox.showinfo("RFID", "Nenhum RFID detectado.")
        except AttributeError:
            # Mensagem para quando o hardware não está conectado/configurado
            messagebox.showinfo("RFID", "Hardware RFID não configurado ou não encontrado.")
            # Para facilitar testes, podemos simular um login
            self.processar_cartao("admin_card_001")


    def processar_cartao(self, codigo_cartao):
        if not codigo_cartao:
            messagebox.showwarning("Entrada Inválida", "Código RFID inválido.")
            return

        usuario = self.carrinho.validar_cartao(codigo_cartao)
        if usuario:
            self.app.usuario_atual = usuario
            self.atualizar_info_usuario_atual()
            messagebox.showinfo("Login", f"Acesso liberado para {usuario.nome}.")
        else:
            self.app.usuario_atual = None
            self.atualizar_info_usuario_atual()
            messagebox.showwarning("Acesso Negado", "Cartão RFID não autorizado!")

    def atualizar_info_usuario_atual(self):
        if self.app.usuario_atual:
            self.label_usuario_atual.config(text=f"Usuário: {self.app.usuario_atual.nome}", foreground=CORES["texto_escuro"])
        else:
            self.label_usuario_atual.config(text="Nenhum usuário identificado", foreground=CORES["alerta"])

    
    def abrir_gavetas_selecionadas(self):
        if not self.app.usuario_atual:
            messagebox.showerror("Acesso Negado", "Faça login com um cartão RFID antes de retirar chaves."); return
        if not self.pecas_selecionadas:
            messagebox.showwarning("Aviso", "Nenhuma chave selecionada."); return

        pecas_db = self.carrinho.listar_todas_pecas()
        pecas_por_gaveta = {}
        for nome in self.pecas_selecionadas:
            peca_encontrada = next((p for p in pecas_db if p.nome == nome), None)
            if peca_encontrada:
                gid = peca_encontrada.gaveta_id
                if gid not in pecas_por_gaveta: pecas_por_gaveta[gid] = []
                pecas_por_gaveta[gid].append(peca_encontrada)

        if not pecas_por_gaveta:
            messagebox.showwarning("Aviso", "Nenhuma chave correspondente encontrada."); return

        gavetas_abertas, gavetas_falharam = [], []
        retiradas_sucesso, retiradas_falha = [], []
        for gaveta_id, pecas_na_gaveta in pecas_por_gaveta.items():
            if self.carrinho.abrir_gaveta(gaveta_id, self.app.usuario_atual.id):
                gavetas_abertas.append(str(gaveta_id))
                for peca in pecas_na_gaveta:
                    if self.carrinho.registrar_retirada_peca(self.app.usuario_atual.id, peca.id, 1):
                        retiradas_sucesso.append(f"1x {peca.nome}")
                    else:
                        retiradas_falha.append(peca.nome)
            else:
                gavetas_falharam.append(str(gaveta_id))

        mensagem = f"Gavetas abertas: {', '.join(gavetas_abertas)}\n\nRetiradas registradas:\n- " + "\n- ".join(retiradas_sucesso)
        if retiradas_falha: mensagem += f"\n\nFalha ao registrar:\n- " + "\n- ".join(retiradas_falha)
        if gavetas_falharam: mensagem += f"\n\nFalha ao abrir gavetas: {', '.join(gavetas_falharam)}"
        messagebox.showinfo("Resultado da Operação", mensagem)

        self.atualizar_status_gavetas()
        if hasattr(self.app, 'aba_inventario'):
            self.app.aba_inventario.atualizar_lista_pecas()
            self.app.aba_inventario.atualizar_pendencias_usuario()
        self.limpar_selecao()

    def fechar_gavetas_abertas(self):
        if not self.app.usuario_atual:
            messagebox.showerror("Acesso Negado", "Realize o login antes de fechar gavetas."); return
        
        gavetas_abertas_ids = [gid for gid, gaveta in self.carrinho.gavetas.items() if gaveta.aberta]
        if not gavetas_abertas_ids:
            messagebox.showinfo("Status", "Nenhuma gaveta está aberta."); return
        
        sucessos, falhas = 0, 0
        for gaveta_id in gavetas_abertas_ids:
            if self.carrinho.fechar_gaveta(gaveta_id, self.app.usuario_atual.id): sucessos += 1
            else: falhas += 1
            
        if sucessos > 0: messagebox.showinfo("Sucesso", f"{sucessos} gaveta(s) fechada(s).")
        if falhas > 0: messagebox.showerror("Erro", f"Falha ao fechar {falhas} gaveta(s).")
        self.atualizar_status_gavetas()
    
    def mostrar_popup_devolucao(self):
        if not self.app.usuario_atual:
            messagebox.showerror("Acesso Negado", "Você precisa estar logado para devolver chaves."); return

        pendencias = self.carrinho.obter_pecas_pendentes_usuario(self.app.usuario_atual.id)
        popup = tk.Toplevel(self.app.root)
        popup.title("Registrar Devolução de Chaves"); popup.geometry("550x350")
        popup.transient(self.app.root); popup.grab_set()
        
        valores_pendencias = []
        if pendencias:
            for ret in pendencias:
                peca = self.carrinho.db.obter_peca_por_id(ret.peca_id)
                nome_peca = peca.nome if peca else f"ID {ret.peca_id}"
                pendente = ret.quantidade_retirada - ret.quantidade_devolvida
                if pendente > 0: valores_pendencias.append(f"{nome_peca} | Pendente: {pendente} [ID Retirada: {ret.id}]")
        
        if not valores_pendencias:
            ttk.Label(popup, text="\nVocê não possui chaves pendentes.", font=FONTES["corpo"]).pack(pady=20)
            ttk.Button(popup, text="Fechar", command=popup.destroy).pack(pady=10); return

        ttk.Label(popup, text="Selecione a chave para devolver:", font=FONTES["subtitulo"]).pack(pady=(20, 10))
        combo_pecas = ttk.Combobox(popup, values=valores_pendencias, width=70, font=FONTES["corpo"], state="readonly")
        combo_pecas.pack(pady=5, padx=20); combo_pecas.set(valores_pendencias[0])
        ttk.Label(popup, text="Quantidade a Devolver:", font=FONTES["corpo"]).pack(pady=(15, 5))
        entry_qtd = ttk.Entry(popup, width=10, font=FONTES["corpo"], justify="center")
        entry_qtd.pack(pady=5); entry_qtd.insert(0, "1")

        def registrar_uma_devolucao():
            try:
                selected = combo_pecas.get()
                if not selected: raise ValueError("Nenhuma chave selecionada.")
                retirada_id = int(selected.split("[ID Retirada:")[1].split("]")[0])
                qtd_pendente = int(selected.split("Pendente: ")[1].split(" [")[0])
                qtd_devolver = int(entry_qtd.get())
                if not (0 < qtd_devolver <= qtd_pendente): raise ValueError(f"Quantidade deve ser entre 1 e {qtd_pendente}.")
            except Exception as e:
                messagebox.showerror("Dados Inválidos", str(e), parent=popup); return

            retirada_obj = next((r for r in pendencias if r.id == retirada_id), None)
            peca = self.carrinho.db.obter_peca_por_id(retirada_obj.peca_id)
            if not peca: messagebox.showerror("Erro", "Chave não encontrada.", parent=popup); return
            
            if not self.carrinho.abrir_gaveta(peca.gaveta_id, self.app.usuario_atual.id):
                messagebox.showerror("Falha na Abertura", f"Não foi possível abrir a Gaveta {peca.gaveta_id}.", parent=popup); return

            if self.carrinho.registrar_devolucao_peca(retirada_id, qtd_devolver):
                messagebox.showinfo("Ação Necessária", f"Gaveta {peca.gaveta_id} aberta.\nDevolva a chave e feche a gaveta.", parent=popup)
                if hasattr(self.app, 'aba_inventario'):
                    self.app.aba_inventario.atualizar_lista_pecas()
                    self.app.aba_inventario.atualizar_pendencias_usuario()
                popup.destroy()
                self.atualizar_status_gavetas()
            else:
                messagebox.showerror("Erro", "Falha ao registrar a devolução.", parent=popup)
                self.carrinho.fechar_gaveta(peca.gaveta_id, self.app.usuario_atual.id)

        frame_botoes = ttk.Frame(popup)
        frame_botoes.pack(pady=20)
        ttk.Button(frame_botoes, text="Devolver e Abrir Gaveta", command=registrar_uma_devolucao, style="Verde.TButton").pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Cancelar", command=popup.destroy, style="Vermelho.TButton").pack(side="left", padx=10)

    def _atualizar_sugestoes(self, event=None):
        texto = self.entry_busca_peca.get().strip().lower()
        self.listbox_sugestoes.delete(0, tk.END)
        if not texto: self.listbox_sugestoes.grid_remove(); return
        try:
            pecas = self.carrinho.listar_todas_pecas()
            sugestoes = [p.nome for p in pecas if texto in p.nome.lower() and p.nome not in self.pecas_selecionadas]
            if sugestoes:
                for nome in sugestoes: self.listbox_sugestoes.insert(tk.END, nome)
                self.listbox_sugestoes.grid()
            else: self.listbox_sugestoes.grid_remove()
        except: self.listbox_sugestoes.grid_remove()

    def _selecionar_sugestao(self, event):
        try:
            indices = self.listbox_sugestoes.curselection()
            if not indices: return
            nome_peca = self.listbox_sugestoes.get(indices[0])
            if nome_peca not in self.pecas_selecionadas:
                self.pecas_selecionadas.append(nome_peca)
                self._adicionar_tag(nome_peca)
            self.entry_busca_peca.delete(0, tk.END)
            self.listbox_sugestoes.grid_remove()
            self.entry_busca_peca.focus()
        except IndexError: pass

    def _adicionar_tag(self, nome_peca):
        tag_frame = tk.Frame(self.frame_tags, bg=CORES["destaque"], bd=1, relief="solid")
        label = tk.Label(tag_frame, text=nome_peca, bg=CORES["destaque"], fg=CORES["texto_claro"], font=FONTES["corpo"])
        label.pack(side="left", padx=(5, 2), pady=2)
        btn = tk.Button(tag_frame, text="x", bg=CORES["destaque"], fg=CORES["texto_claro"], relief="flat", bd=0, cursor="hand2", command=lambda p=nome_peca, tf=tag_frame: self._remover_tag(p, tf))
        btn.pack(side="left", padx=(2, 5))
        tag_frame.pack(side="left", padx=2, pady=2)

    def _remover_tag(self, nome_peca, tag_frame):
        if nome_peca in self.pecas_selecionadas: self.pecas_selecionadas.remove(nome_peca)
        tag_frame.destroy()

    def limpar_selecao(self):
        for widget in self.frame_tags.winfo_children(): widget.destroy()
        self.pecas_selecionadas.clear()
        self.entry_busca_peca.delete(0, tk.END)
        self.listbox_sugestoes.grid_remove()

    def _esconder_sugestoes_se_clicar_fora(self, event):
        if event.widget != self.entry_busca_peca and event.widget != self.listbox_sugestoes:
            self.listbox_sugestoes.grid_remove()
    
    def abrir_todas_gavetas_admin(self):
        if not self.app.usuario_atual:
            messagebox.showerror("Acesso Negado", "Apenas administradores logados podem usar esta função."); return

        confirmar = messagebox.askyesno("Ação de Administrador", "Deseja destravar TODAS as gavetas?", icon='warning')
        if confirmar:
            if self.carrinho.abrir_todas_gavetas_manutencao(self.app.usuario_atual.id):
                messagebox.showinfo("Sucesso", "Todas as gavetas foram destravadas.")
            else: messagebox.showerror("Erro", "Falha ao destravar as gavetas.")
            self.atualizar_status_gavetas()
    
    def atualizar_status_gavetas(self):
        for gaveta_id, gaveta in self.carrinho.gavetas.items():
            label = self.labels_status_gavetas.get(gaveta_id)
            if label:
                if gaveta.aberta:
                    try:
                        tempo_aberta = int(gaveta.tempo_aberta())
                        texto_tempo = f" (aberta há {tempo_aberta//60}m {tempo_aberta%60}s)"
                        label.config(text=f"Gaveta {gaveta_id}: ABERTA{texto_tempo}", foreground=CORES["alerta"])
                    except:
                         label.config(text=f"Gaveta {gaveta_id}: ABERTA", foreground=CORES["alerta"])
                else:
                    label.config(text=f"Gaveta {gaveta_id}: FECHADA", foreground='green')