import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import CORES, FONTES

class AbaPrincipal(ttk.Frame):
    """Frame que contém a funcionalidade principal de retirada de peças."""
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent)
        self.carrinho = carrinho_controller
        self.app = app_controller  

        self.labels_status_gavetas = {}
        self.setup_widgets()
        self.atualizar_status_gavetas()
       # self.atualizar_info_usuario_atual() 

    def setup_widgets(self):
        style = ttk.Style()
        style.configure(
            "Verde.TButton",
            font=FONTES["botao"],
            background=CORES["sucesso"],
            foreground=CORES["texto_claro"]
        )
        style.map('Verde.TButton', background=[('active', '#27ae60')])
        
        style.configure(
            "Azul.TButton",
            font=FONTES["botao"],
            background=CORES["destaque"],
            foreground=CORES["texto_claro"]
        )
        style.map('Azul.TButton', background=[('active', '#2980b9')])
        
        cor_vermelha = CORES.get("cancelar", "#e74c3c")
        cor_vermelha_active = CORES.get("cancelar_active", "#c0392b")
        style.configure("Vermelho.TButton",
                        font=FONTES["botao"],
                        background=cor_vermelha,
                        foreground=CORES["texto_claro"])
        style.map("Vermelho.TButton",
                  background=[('active', cor_vermelha_active)])

        style.configure("Alerta.TButton",
                        font=FONTES["botao"],
                        background=CORES["alerta"],
                        foreground=CORES["texto_claro"])
        style.map("Alerta.TButton",
                  background=[('active', '#e67e22')]) 

        #frame_rfid = ttk.LabelFrame(self, text="Acesso por RFID")
        #frame_rfid.pack(fill='x', padx=10, pady=10, ipady=10)

        #self.label_usuario_atual = ttk.Label(frame_rfid, text="Nenhum usuário identificado", foreground=CORES["alerta"])
        #self.label_usuario_atual.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

        #ttk.Button(frame_rfid, text="Ler RFID (Login)", command=self.ler_rfid).grid(row=0, column=2, padx=10, pady=10)

        # Frame de Busca de Peça
        frame_busca = ttk.LabelFrame(self, text="Buscar Peça para Retirada")
        frame_busca.pack(fill='x', padx=10, pady=10, ipady=10)

        ttk.Label(frame_busca, text="Nome da Peça:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.entry_busca_peca = ttk.Entry(frame_busca, width=40, font=FONTES["corpo"])
        self.entry_busca_peca.grid(row=0, column=1, padx=10, pady=10, ipady=5)
        self.entry_busca_peca.bind('<Return>', self.buscar_e_abrir_gaveta)

        ttk.Button(frame_busca, text="Buscar e Abrir Gaveta", command=self.buscar_e_abrir_gaveta, style="Verde.TButton").grid(row=0, column=2, padx=10, pady=10, ipady=5)

        # Frame para o botão de devolução
        frame_acoes = ttk.LabelFrame(self, text="Ações do Usuário")
        frame_acoes.pack(fill='x', padx=10, pady=10, ipady=10)

        ttk.Button(
            frame_acoes, 
            text="Devolver Peças", 
            command=self.mostrar_popup_devolucao, 
            style="Azul.TButton"
        ).pack(side="left", padx=10, pady=5)

        self.botao_abrir_todas = ttk.Button(
            frame_acoes, 
            text="Abrir Todas as Gavetas (Admin)", 
            command=self.abrir_todas_gavetas_admin, 
            style="Alerta.TButton"
        )

        # Frame de Status das Gavetas
        frame_status = ttk.LabelFrame(self, text="Status das Gavetas")
        frame_status.pack(fill='both', expand=True, padx=10, pady=10)

        for i in range(1, 6):
            lbl = ttk.Label(frame_status, text=f"Gaveta {i}: FECHADA", foreground='green', font=FONTES["subtitulo"])
            lbl.pack(anchor='w', pady=5, padx=10)
            self.labels_status_gavetas[i] = lbl

    def abrir_todas_gavetas_admin(self):
        confirmar = messagebox.askyesno(
            "Ação de Administrador",
            "Você está prestes a destravar TODAS as gavetas para manutenção.\n\nDeseja continuar?",
            icon='warning'
        )
        if confirmar:
            sucesso = self.carrinho.abrir_todas_gavetas_manutencao(self.app.usuario_atual.id)
            if sucesso:
                messagebox.showinfo("Sucesso", "Todas as gavetas foram destravadas.")
            else:
                messagebox.showerror("Erro", "Falha ao destravar as gavetas. Verifique as permissões.")
            self.atualizar_status_gavetas()

    def ler_rfid(self):
        try:
            codigo = self.carrinho.hardware.ler_rfid() or "admin_card_001" 
            if codigo:
                self.processar_cartao(codigo)
            else:
                messagebox.showinfo("RFID", "Nenhum RFID detectado.")
        except AttributeError:
            messagebox.showinfo("RFID", "Hardware RFID não configurado.")

    def processar_cartao(self, codigo_cartao):
        if not codigo_cartao:
            messagebox.showwarning("Entrada Inválida", "Código RFID inválido.")
            return

        usuario = self.carrinho.validar_cartao(codigo_cartao)
        if usuario:
            self.app.usuario_atual = usuario
            self.atualizar_info_usuario_atual()
            self.app.configurar_acesso_por_perfil(usuario.perfil)
            self.app.label_usuario_header.config(text=f"Bem-vindo, {usuario.nome}!", fg=CORES["texto_claro"])
            messagebox.showinfo("Login", f"Acesso liberado para {usuario.nome}.")
        else:
            self.app.usuario_atual = None
            self.atualizar_info_usuario_atual()
            self.app.configurar_acesso_por_perfil(None)
            messagebox.showwarning("Acesso Negado", "Cartão RFID não autorizado!")

    def atualizar_info_usuario_atual(self):
        if self.app.usuario_atual:
            self.label_usuario_atual.config(text=f"Usuário: {self.app.usuario_atual.nome}", foreground=CORES["texto_escuro"])
        else:
            self.label_usuario_atual.config(text="Nenhum usuário identificado", foreground=CORES["alerta"])

    def buscar_e_abrir_gaveta(self, event=None):
        if not self.app.usuario_atual:
            messagebox.showerror("Acesso Negado", "Realize o login com um cartão autorizado antes de retirar uma peça.")
            return

        nome_peca = self.entry_busca_peca.get().strip()
        if not nome_peca:
            messagebox.showwarning("Entrada Inválida", "Digite o nome da peça para buscar.")
            return

        pecas = self.carrinho.listar_todas_pecas()
        peca_encontrada = next((p for p in pecas if nome_peca.lower() in p.nome.lower()), None)

        if not peca_encontrada:
            messagebox.showerror("Não Encontrado", f"Peça '{nome_peca}' não encontrada no inventário.")
            return

        gaveta_id = peca_encontrada.gaveta_id
        if self.carrinho.gavetas[gaveta_id].aberta:
            messagebox.showinfo("Aviso", f"A Gaveta {gaveta_id} já está aberta.")
            return

        sucesso = self.carrinho.abrir_gaveta(gaveta_id, self.app.usuario_atual.id)
        if sucesso:
            messagebox.showinfo("Sucesso", f"Gaveta {gaveta_id} aberta para a peça '{peca_encontrada.nome}'.")
            self.mostrar_pop_up_retirada(gaveta_id)
        else:
            messagebox.showerror("Erro", f"Falha ao abrir Gaveta {gaveta_id}. Verifique se não há outra gaveta aberta.")

        self.atualizar_status_gavetas()
        self.entry_busca_peca.delete(0, tk.END)

    def mostrar_pop_up_retirada(self, gaveta_id):
        popup = tk.Toplevel(self.app.root)
        popup.title(f"Registrar Retirada - Gaveta {gaveta_id}")
        popup.geometry("450x350")
        popup.transient(self.app.root)
        popup.grab_set()
        popup.configure(bg=CORES["fundo_widget"])

        ttk.Label(popup, text=f"Peças disponíveis na Gaveta {gaveta_id}:", font=FONTES["subtitulo"]).pack(pady=(20, 10))

        pecas = self.carrinho.listar_pecas_por_gaveta(gaveta_id)
        if not pecas:
            return

        valores_pecas = [f"{p.nome} (Estoque: {p.quantidade_disponivel}) [ID: {p.id}]" for p in pecas]
        combo_retirada_peca = ttk.Combobox(popup, values=valores_pecas, width=40, font=FONTES["corpo"], state="readonly")
        combo_retirada_peca.pack(pady=5, padx=20, ipady=4)
        if valores_pecas:
            combo_retirada_peca.set(valores_pecas[0])

        ttk.Label(popup, text="Quantidade a Retirar:", font=FONTES["corpo"]).pack(pady=(10, 5))
        entry_retirada_qtd = ttk.Entry(popup, width=10, font=FONTES["corpo"], justify="center")
        entry_retirada_qtd.pack(pady=5)
        entry_retirada_qtd.insert(0, "1")

        def fechar_gaveta():
            usuario_id = self.app.usuario_atual.id if self.app.usuario_atual else None
            if self.carrinho.fechar_gaveta(gaveta_id, usuario_id):
                messagebox.showinfo("Gaveta Fechada", f"Gaveta {gaveta_id} fechada com sucesso.", parent=popup)
                popup.destroy()
                self.atualizar_status_gavetas()
            else:
                messagebox.showerror("Erro", "Falha ao fechar gaveta.", parent=popup)

        def registrar_uma_retirada():
            try:
                selected = combo_retirada_peca.get()
                if not selected: raise ValueError("Nenhuma peça selecionada")
                peca_id = int(selected.split("[ID:")[1].split("]")[0])
                qtd = int(entry_retirada_qtd.get())
            except (ValueError, IndexError):
                return

            peca = self.carrinho.db.obter_peca_por_id(peca_id)
            if not peca or qtd <= 0 or peca.quantidade_disponivel < qtd:
                return

            if self.carrinho.registrar_retirada_peca(self.app.usuario_atual.id, peca_id, qtd):
                messagebox.showinfo("Sucesso", f"{qtd} unidades de '{peca.nome}' retiradas!\nA gaveta será fechada.", parent=popup)
                
                self.app.aba_inventario.atualizar_lista_pecas()
                self.app.aba_inventario.atualizar_pendencias_usuario()
                
                fechar_gaveta()
            else:
                messagebox.showerror("Erro", "Falha ao registrar retirada.", parent=popup)
        
        frame_botoes = ttk.Frame(popup)
        frame_botoes.pack(pady=20)
        
        ttk.Button(frame_botoes, text="Confirmar Retirada", command=registrar_uma_retirada, style="Verde.TButton").pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Apenas Fechar Gaveta", command=fechar_gaveta, style="Azul.TButton").pack(side="left", padx=10)

    def mostrar_popup_devolucao(self):
        if not self.app.usuario_atual:
            messagebox.showerror("Acesso Negado", "Você precisa estar logado para devolver peças.")
            return

        pendencias = self.carrinho.obter_pecas_pendentes_usuario(self.app.usuario_atual.id)

        popup = tk.Toplevel(self.app.root)
        popup.title("Registrar Devolução de Peças")
        popup.geometry("500x350")
        popup.transient(self.app.root)
        popup.grab_set()
        
        if not pendencias:
            ttk.Label(popup, text="\nVocê não possui peças pendentes para devolução.", font=FONTES["corpo"]).pack(pady=20)
            ttk.Button(popup, text="Fechar", command=popup.destroy).pack(pady=10)
            return

        ttk.Label(popup, text="Selecione a peça para devolver:", font=FONTES["subtitulo"]).pack(pady=(20, 10))

        valores_pendencias = []
        for ret in pendencias:
            peca = self.carrinho.db.obter_peca_por_id(ret.peca_id)
            nome_peca = peca.nome if peca else f"ID {ret.peca_id}"
            pendente = ret.quantidade_retirada - ret.quantidade_devolvida
            valores_pendencias.append(f"{nome_peca} | Pendente: {pendente} [ID Retirada: {ret.id}]")
        
        combo_pecas = ttk.Combobox(popup, values=valores_pendencias, width=60, font=FONTES["corpo"], state="readonly")
        combo_pecas.pack(pady=5, padx=20)
        if valores_pendencias:
            combo_pecas.set(valores_pendencias[0])

        ttk.Label(popup, text="Quantidade a Devolver:", font=FONTES["corpo"]).pack(pady=(15, 5))
        entry_qtd = ttk.Entry(popup, width=10, font=FONTES["corpo"], justify="center")
        entry_qtd.pack(pady=5)
        entry_qtd.insert(0, "1")

        def registrar_uma_devolucao():
            try:
                selected = combo_pecas.get()
                if not selected: raise ValueError("Nenhuma peça selecionada")
                
                retirada_id = int(selected.split("[ID Retirada:")[1].split("]")[0])
                qtd_pendente = int(selected.split("Pendente: ")[1].split(" [")[0])
                qtd_devolver = int(entry_qtd.get())

                if qtd_devolver <= 0 or qtd_devolver > qtd_pendente:
                    raise ValueError(f"A quantidade deve ser entre 1 e {qtd_pendente}.")

            except Exception as e:
                messagebox.showerror("Dados Inválidos", str(e), parent=popup)
                return

            if self.carrinho.registrar_devolucao_peca(retirada_id, qtd_devolver):
                messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!", parent=popup)
                self.app.aba_inventario.atualizar_lista_pecas()
                self.app.aba_inventario.atualizar_pendencias_usuario()
                popup.destroy()
            else:
                messagebox.showerror("Erro", "Falha ao registrar a devolução.", parent=popup)

        frame_botoes = ttk.Frame(popup)
        frame_botoes.pack(pady=20)

        ttk.Button(frame_botoes, text="Registrar Devolução", command=registrar_uma_devolucao, style="Verde.TButton").pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Cancelar", command=popup.destroy, style="Vermelho.TButton").pack(side="left", padx=10)

    def atualizar_status_gavetas(self):
        for gaveta_id, gaveta in self.carrinho.gavetas.items():
            label = self.labels_status_gavetas.get(gaveta_id)
            if label:
                if gaveta.aberta:
                    tempo_aberta = gaveta.tempo_aberta()
                    texto_tempo = f" (aberta há {tempo_aberta//60}m {tempo_aberta%60}s)"
                    label.config(text=f"Gaveta {gaveta_id}: ABERTA{texto_tempo}", foreground=CORES["alerta"])
                else:
                    label.config(text=f"Gaveta {gaveta_id}: FECHADA", foreground='green')