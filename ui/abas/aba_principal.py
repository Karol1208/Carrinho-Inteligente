import customtkinter as ctk
from tkinter import messagebox
from ui.theme import CORES, FONTES
from ui.components.glass_card import GlassCard
from ui.components.search_results import SearchResultsList
from PIL import Image
import os

class AbaPrincipal(ctk.CTkFrame):
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.carrinho = carrinho_controller
        self.app = app_controller
        self.labels_status_gavetas = {}
        self.pecas_selecionadas = []
        self.icones = {}
        self.carregar_icones()

        self.setup_widgets()
        self.atualizar_status_gavetas()

    def setup_widgets(self):
        # Container Principal com Scroll
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # --- BUSCA DE CHAVES ---
        busca_card = GlassCard(self.main_container)
        busca_card.pack(fill="x", padx=0, pady=0)
        
        
        ctk.CTkLabel(busca_card, text= "🔍 Buscar Chave para Retirada", font=FONTES["subtitulo"]).pack(pady=(10, 10))

        self.frame_tags = ctk.CTkFrame(busca_card, fg_color="transparent")
        self.frame_tags.pack(fill="x", padx=10, pady=5)

        search_row = ctk.CTkFrame(busca_card, fg_color="transparent")
        search_row.pack(fill="x", padx=10, pady=10)

        self.entry_busca_peca = ctk.CTkEntry(
            search_row, 
            placeholder_text="Digite o nome da ferramenta...",
            height=45,
            font=FONTES["corpo"]
        )
        self.entry_busca_peca.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_busca_peca.bind("<KeyRelease>", self._atualizar_sugestoes)

        self.results_list = SearchResultsList(busca_card, self._selecionar_sugestao_combo)
        # Oculto inicialmente, aparece ao digitar

        # Botoes de Ação
        btn_row = ctk.CTkFrame(busca_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=15)

        self.btn_abrir = ctk.CTkButton(
            btn_row, 
            text="ABRIR GAVETAS E REGISTRAR", 
            fg_color=CORES["sucesso"],
            hover_color="#27ae60",
            font=FONTES["botao"],
            command=self.abrir_gavetas_selecionadas
        )
        self.btn_abrir.pack(side="right", padx=5)

        self.btn_limpar = ctk.CTkButton(
            btn_row, 
            text="Limpar Seleção", 
            fg_color=CORES["cancelar"],
            hover_color="#c0392b",
            font=FONTES["botao"],
            command=self.limpar_selecao
        )
        self.btn_limpar.pack(side="right", padx=5)

        # --- AÇÕES RÁPIDAS ---
        acoes_card = GlassCard(self.main_container)
        acoes_card.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(acoes_card, text="⚡ Ações Rápidas", font=FONTES["subtitulo"]).pack(pady=(15, 10))

        btn_row_acoes = ctk.CTkFrame(acoes_card, fg_color="transparent")
        btn_row_acoes.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(
            btn_row_acoes, 
            text="Devolver Chave", 
            fg_color=CORES["destaque"],
            hover_color=CORES["destaque_hover"],
            font=FONTES["botao"],
            command=self.mostrar_popup_devolucao
        ).pack(side="left", padx=5)

        self.botao_abrir_todas = ctk.CTkButton(
            btn_row_acoes, 
            text="Manutenção: Abrir Tudo", 
            fg_color=CORES["alerta"],
            text_color="black",
            hover_color="#e67e22",
            font=FONTES["botao"],
            command=self.abrir_todas_gavetas_admin
        )
        # Exibe o botão de manutenção apenas para admins
        if hasattr(self.app, 'usuario_atual') and self.app.usuario_atual and self.app.usuario_atual.perfil == 'admin':
            self.botao_abrir_todas.pack(side="left", padx=5)

        # --- STATUS DAS GAVETAS ---
        status_card = GlassCard(self.main_container)
        status_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(status_card, text="📊 Status das Gavetas (Sensores IR)", font=FONTES["subtitulo"]).pack(pady=(15, 10))

        self.status_grid = ctk.CTkFrame(status_card, fg_color="transparent")
        self.status_grid.pack(fill="both", expand=True, padx=20, pady=10)

        for i in range(1, 8):
            lbl = ctk.CTkLabel(
                self.status_grid, 
                text=f"Gaveta {i}: Verificando...", 
                font=FONTES["corpo"],
                text_color=CORES["texto_muted"]
            )
            lbl.pack(anchor="w", pady=2)
            self.labels_status_gavetas[i] = lbl

        self.label_sensor_ir = ctk.CTkLabel(
            status_card, 
            text="Sistema de monitoramento ativo", 
            font=FONTES["corpo"],
            text_color=CORES["sucesso"]
        )
        self.label_sensor_ir.pack(pady=10)

    def carregar_icones(self):
        try:
            icon_data = Image.open("assets/icon_home.png")
            self.icones["gaveta"] = ctk.CTkImage(light_image=icon_data, dark_image=icon_data, size=(20, 20))
        except Exception:
            pass

    def _atualizar_sugestoes(self, event=None):
        texto = self.entry_busca_peca.get().strip().lower()
        if not texto:
            self.results_list.pack_forget()
            return
        
        pecas = self.carrinho.listar_todas_pecas()
        sugestoes = []
        for p in pecas:
            if texto in p.nome.lower() and p.nome not in self.pecas_selecionadas:
                if p.nome not in sugestoes:
                    sugestoes.append(p.nome)
        
        if sugestoes:
            self.results_list.atualizar_resultados(sugestoes[:5])
            self.results_list.pack(fill="x", padx=20, pady=(0, 10))
        else:
            self.results_list.pack_forget()

    def _selecionar_sugestao_combo(self, nome_peca):
        if nome_peca not in self.pecas_selecionadas:
            self.pecas_selecionadas.append(nome_peca)
            self._adicionar_tag(nome_peca)
        self.entry_busca_peca.delete(0, 'end')

    def _adicionar_tag(self, nome_peca):
        tag = ctk.CTkFrame(self.frame_tags, fg_color=CORES["destaque"], corner_radius=15)
        tag.pack(side="left", padx=5, pady=5)
        
        ctk.CTkLabel(tag, text=nome_peca, font=FONTES["corpo"], text_color="white").pack(side="left", padx=(10, 5), pady=2)
        
        btn_close = ctk.CTkButton(
            tag, text="✕", width=20, height=20, 
            fg_color="transparent", hover_color=CORES["destaque_hover"],
            command=lambda p=nome_peca, t=tag: self._remover_tag(p, t)
        )
        btn_close.pack(side="left", padx=(0, 5))

    def _remover_tag(self, nome_peca, tag_widget):
        if nome_peca in self.pecas_selecionadas:
            self.pecas_selecionadas.remove(nome_peca)
        tag_widget.destroy()

    def limpar_selecao(self):
        for widget in self.frame_tags.winfo_children():
            widget.destroy()
        self.pecas_selecionadas.clear()
        self.entry_busca_peca.delete(0, 'end')

    def abrir_gavetas_selecionadas(self):
        if not self.app.usuario_atual:
            messagebox.showerror("Acesso Negado", "Autentique-se antes de retirar ferramentas.")
            return
        if not self.pecas_selecionadas:
            messagebox.showwarning("Aviso", "Selecione ao menos uma chave.")
            return

        pecas_db = self.carrinho.listar_todas_pecas()
        pecas_por_gaveta = {}
        for nome in self.pecas_selecionadas:
            peca = next((p for p in pecas_db if p.nome == nome), None)
            if peca:
                gid = peca.gaveta_id
                if gid not in pecas_por_gaveta: pecas_por_gaveta[gid] = []
                pecas_por_gaveta[gid].append(peca)

        if not pecas_por_gaveta: return

        gavetas_abertas = []
        for gid, pecas in pecas_por_gaveta.items():
            sucesso_reg = False
            for p in pecas:
                if self.carrinho.registrar_retirada_peca(self.app.usuario_atual.id, p.id, 1):
                    sucesso_reg = True
            
            if sucesso_reg:
                if self.carrinho.abrir_gaveta(gid, self.app.usuario_atual.id):
                    gavetas_abertas.append(str(gid))

        if gavetas_abertas:
            messagebox.showinfo("Operação Concluída", f"Gavetas {', '.join(gavetas_abertas)} destravadas com sucesso.")
        
        self.atualizar_status_gavetas()
        self.limpar_selecao()

    def mostrar_popup_devolucao(self):
        if not self.app.usuario_atual:
            messagebox.showerror("Erro", "Usuário não identificado.")
            return

        pendencias = self.carrinho.obter_pecas_pendentes_usuario(self.app.usuario_atual.id)
        if not pendencias:
            messagebox.showinfo("Status", "Você não possui chaves pendentes.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Devolução Múltipla")
        popup.geometry("600x550")
        popup.configure(fg_color=CORES["fundo_principal"])
        
        try:
            import os
            ico_path = os.path.abspath("assets/crdf_icon.ico")
            popup.after(100, lambda: popup.iconbitmap(ico_path))
        except: pass
        
        popup.grab_set()

        ctk.CTkLabel(popup, text="Selecione os itens para devolver", font=FONTES["subtitulo"]).pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        checkboxes = {}
        for ret in pendencias:
            peca = self.carrinho.db.obter_peca_por_id(ret.peca_id)
            nome = peca.nome if peca else f"ID {ret.peca_id}"
            pendente = ret.quantidade_retirada - ret.quantidade_devolvida
            
            f = ctk.CTkFrame(scroll, fg_color=CORES["fundo_secundario"])
            f.pack(fill="x", pady=5, padx=5)
            
            cb = ctk.CTkCheckBox(f, text=f"{nome} (Pendente: {pendente})", font=FONTES["corpo"])
            cb.pack(side="left", padx=15, pady=12)
            checkboxes[ret.id] = (cb, peca.gaveta_id if peca else None)

        def confirmar_devolucao():
            selecionados = []
            for r_id, (cb, g_id) in checkboxes.items():
                if cb.get():
                    selecionados.append((r_id, g_id))
            
            if not selecionados:
                messagebox.showwarning("Aviso", "Selecione ao menos um item.")
                return
            
            sucesso_algum = False
            gavetas_abertas = set()
            for r_id, g_id in selecionados:
                if self.carrinho.registrar_devolucao_peca(r_id, 1):
                    sucesso_algum = True
                    if g_id:
                        self.carrinho.abrir_gaveta(g_id, self.app.usuario_atual.id)
                        gavetas_abertas.add(str(g_id))
            
            if sucesso_algum:
                msg = f"Devolução registrada!"
                if gavetas_abertas:
                    msg += f"\nGavetas abertas: {', '.join(gavetas_abertas)}"
                messagebox.showinfo("Sucesso", msg)
                popup.destroy()
                self.atualizar_status_gavetas()
            else:
                messagebox.showerror("Erro", "Falha ao processar devolução.")

        btn_confirmar = ctk.CTkButton(
            popup, text="CONFIRMAR DEVOLUÇÃO", 
            fg_color=CORES["sucesso"], height=45, font=FONTES["botao"],
            command=confirmar_devolucao
        )
        btn_confirmar.pack(pady=20)


    def abrir_todas_gavetas_admin(self):
        if messagebox.askyesno("Confirmar", "Deseja destravar TODAS as gavetas para manutenção?"):
            if self.carrinho.abrir_todas_gavetas_manutencao(self.app.usuario_atual.id):
                messagebox.showinfo("Manutenção", "Todas as gavetas foram abertas.")
            self.atualizar_status_gavetas()

    def atualizar_status_gavetas(self):
        for gid, lbl in self.labels_status_gavetas.items():
            gaveta = self.carrinho.gavetas.get(gid)
            if not gaveta: continue
            
            if gaveta.aberta:
                lbl.configure(text=f"Gaveta {gid}: ⚠ ABERTA", text_color=CORES["alerta"])
            else:
                lbl.configure(text=f"Gaveta {gid}: ✅ FECHADA", text_color=CORES["sucesso"])