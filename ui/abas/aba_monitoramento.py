import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime
from collections import Counter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import CORES, FONTES
from ui.components.glass_card import GlassCard
from ui.components.tabela_pro import TabelaPRO
import threading
from PIL import Image
import os

class AbaMonitoramento(ctk.CTkFrame):
    """Painel de dashboard com gráficos Matplotlib funcionais, inspirado no layout moderno."""

    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.carrinho = carrinho_controller
        self.app = app_controller

        self._last_data_hash = None
        self._setup_widgets()
        
        # Inicia a atualização em background (Evitar travar main thread)
        self.atualizar_dashboard_assincrono()

    def _setup_widgets(self):
        """Cria e organiza os widgets na janela com layout de dashboard premium."""
        
        # 1. Header do Dashboard (Removido os botões de fechar e título Toplevel, pois será abas)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(side="top", fill="x", padx=10, pady=(10, 10))
        
        try: title_icon = ctk.CTkImage(Image.open("assets/crdf_icon.png"), size=(28, 28))
        except: title_icon = None
        
        ctk.CTkLabel(
            header_frame, 
            text=" Análise de Peças Pendentes em Tempo Real", 
            image=title_icon,
            compound="left",
            font=("Segoe UI Variable", 24, "bold"),
            text_color=CORES["texto_claro"]
        ).pack(side="left")

        # 2. Scrollable Container para o Conteúdo
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # 3. LINHA DOS KPIS (Cards Superiores)
        kpi_row = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        kpi_row.pack(fill="x", pady=10)

        # Função auxiliar para carregar imagem ou silenciosamente falhar
        def load_icon(name):
            try: return ctk.CTkImage(Image.open(f"assets/{name}"), size=(24, 24))
            except: return None
            
        icon_box = load_icon("total_pendente.png")
        icon_warn = load_icon("user_critico.png")
        icon_time = load_icon("antigo.png")
        icon_danger = load_icon("atraso.png") # Ou algum de alerta
            
        self.kpi_total = self._criar_kpi_card(kpi_row, "Total Pendente", icon_box)
        self.kpi_critico = self._criar_kpi_card(kpi_row, "Usuário Crítico", icon_warn)
        self.kpi_antigo = self._criar_kpi_card(kpi_row, "Item Mais Antigo", icon_time)
        self.kpi_alerta = self._criar_kpi_card(kpi_row, "Atraso > 2 Dias", icon_danger)

        # 4. LINHA DOS GRÁFICOS
        charts_row = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        charts_row.pack(fill="x", pady=10)

        # Card Gráfico de Barras
        bar_card = GlassCard(charts_row)
        bar_card.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(bar_card, text="Top 5 Peças Mais Pendentes", font=FONTES["subtitulo"]).pack(pady=10)
        
        self.fig_bar = Figure(figsize=(5, 3), dpi=100, facecolor=CORES["fundo_card"])
        self.ax_bar = self.fig_bar.add_subplot(111)
        self.ax_bar.set_facecolor(CORES["fundo_card"])
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, master=bar_card)
        self.canvas_bar.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

        # Card Gráfico de Pizza
        pie_card = GlassCard(charts_row)
        pie_card.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(pie_card, text="Distribuição por Usuário", font=FONTES["subtitulo"]).pack(pady=10)
        
        self.fig_pie = Figure(figsize=(4, 3), dpi=100, facecolor=CORES["fundo_card"])
        self.ax_pie = self.fig_pie.add_subplot(111)
        self.ax_pie.set_facecolor(CORES["fundo_card"])
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, master=pie_card)
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

        # 5. TABELA DETALHADA
        table_card = GlassCard(self.main_scroll)
        table_card.pack(fill="both", expand=True, padx=10, pady=20)
        ctk.CTkLabel(table_card, text="Detalhamento das Pendências", font=FONTES["subtitulo"]).pack(pady=10)

        # TabelaPRO - Padrão Global Aplicado
        self.tabela_monitoramento = TabelaPRO(
            table_card,
            columns=["Usuário", "Chave / Ferramenta", "Qtd.", "Tempo Decorrido"],
            col_widths=[2, 3, 1, 2],
            show_actions=False
        )
        self.tabela_monitoramento.pack(fill="both", expand=True, padx=20, pady=15)

    def _criar_kpi_card(self, parent, titulo, image_obj):
        card = GlassCard(parent)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(pady=(15, 5))
        
        if image_obj:
            ctk.CTkLabel(header_frame, text="", image=image_obj).pack(side="left", padx=(0, 5))
            
        ctk.CTkLabel(header_frame, text=titulo, font=FONTES["corpo"], text_color=CORES["texto_muted"]).pack(side="left")
        
        val_label = ctk.CTkLabel(card, text="-", font=FONTES["kpi"], text_color=CORES["destaque"])
        val_label.pack(pady=(0, 15))
        return val_label

    def _desenhar_grafico_barras(self, dados):
        self.ax_bar.clear()
        self.ax_bar.tick_params(colors=CORES["texto_muted"], labelsize=8)
        for spine in self.ax_bar.spines.values(): spine.set_color(CORES["glass_borda"])
        
        if not dados:
            self.ax_bar.text(0.5, 0.5, "Sem dados", ha='center', va='center', color=CORES["texto_muted"])
        else:
            pecas = [p[:15] + '...' if len(p) > 15 else p for p in dados.keys()]
            quantidades = list(dados.values())
            self.ax_bar.barh(pecas, quantidades, color=CORES["destaque"])
            self.ax_bar.invert_yaxis()
        
        self.fig_bar.tight_layout()
        self.canvas_bar.draw_idle()  # draw_idle para maior fluidez
        
    def _desenhar_grafico_pizza(self, dados):
        self.ax_pie.clear()
        if not dados:
            self.ax_pie.text(0.5, 0.5, "Sem dados", ha='center', va='center', color=CORES["texto_muted"])
        else:
            labels = list(dados.keys())
            sizes = list(dados.values())
            cores = [CORES["destaque"], CORES["gradiente_2"], "#e67e22"]
            
            self.ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                           wedgeprops=dict(width=0.4, edgecolor=CORES["fundo_card"]),
                           colors=cores[:len(labels)],
                           textprops={'fontsize': 8, 'color': CORES["texto_claro"]})

        self.fig_pie.tight_layout()
        self.canvas_pie.draw_idle()

    def atualizar_dashboard_assincrono(self):
        # Executa a busca no banco de dados através de uma thread para não travar a UI
        threading.Thread(target=self._processar_dados, daemon=True).start()
        
        # Agenda próxima execução via safe_after do app controller para não criar vazamento de memoria se destruir aba
        if hasattr(self.app, 'safe_after'):
            self.app.safe_after(20000, self.atualizar_dashboard_assincrono)
        else:
            self.after(20000, self.atualizar_dashboard_assincrono)

    def _processar_dados(self):
        try:
            pendencias = [p for p in self.carrinho.db.obter_todas_retiradas_pendentes() if (p.quantidade_retirada - p.quantidade_devolvida) > 0]
            
            # Extrai os dados puros para hash rápido
            estado_atual = tuple((p.id, p.usuario_id, p.quantidade_retirada, p.quantidade_devolvida) for p in pendencias)
            novo_hash = hash(estado_atual)
            
            # Otimização UX/UI: Se nada mudou literalmente no mundo real, ABORTA o rebuild brutal do gráfico e tabelas
            if novo_hash == getattr(self, '_last_data_hash', None):
                return
            
            self._last_data_hash = novo_hash

            total_pecas = 0; usuarios_counter = Counter(); pecas_counter = Counter()
            peca_antiga = "Nenhuma"; itens_criticos = 0; max_delta = datetime.timedelta(0)
            
            dados_tabela = []

            for ret in pendencias:
                usuario = self.carrinho.db.obter_usuario_por_id(ret.usuario_id)
                peca = self.carrinho.db.obter_peca_por_id(ret.peca_id)
                nome_u = usuario.nome if usuario else f"ID {ret.usuario_id}"
                nome_p = peca.nome if peca else f"ID {ret.peca_id}"
                qtd = ret.quantidade_retirada - ret.quantidade_devolvida
                
                total_pecas += qtd
                usuarios_counter[nome_u] += qtd
                pecas_counter[nome_p] += qtd
                
                ts = datetime.datetime.fromisoformat(ret.timestamp_retirada)
                delta = datetime.datetime.now() - ts
                if delta.days >= 2: itens_criticos += qtd
                if delta > max_delta: 
                    max_delta = delta
                    peca_antiga = f"{nome_p} ({self.formatar_tempo_decorrido(delta)})"
                
                dados_tabela.append((nome_u, nome_p, qtd, self.formatar_tempo_decorrido(delta)))

            # Volta pra thread principal para modificar a Interface
            self.after(0, lambda: self._aplicar_dados_na_ui(
                total_pecas, usuarios_counter, pecas_counter, 
                peca_antiga, itens_criticos, dados_tabela
            ))

        except Exception as e:
            print(f"ERRO Dashboard: {e}")

    def _aplicar_dados_na_ui(self, total_pecas, usuarios_counter, pecas_counter, peca_antiga, itens_criticos, dados_tabela):
        if not self.winfo_exists(): return
        
        # Aplica kpis
        self.kpi_total.configure(text=str(total_pecas))
        self.kpi_critico.configure(text=usuarios_counter.most_common(1)[0][0] if usuarios_counter else "Nenhum")
        self.kpi_antigo.configure(text=peca_antiga)
        self.kpi_alerta.configure(text=str(itens_criticos), text_color=CORES["cancelar"] if itens_criticos > 0 else CORES["destaque"])
        
        # Recria tabela
        self.tabela_monitoramento.carregar(dados_tabela)
            
        # Graficos
        self._desenhar_grafico_barras(dict(pecas_counter.most_common(5)))
        self._desenhar_grafico_pizza(dict(usuarios_counter.most_common(3)))

    @staticmethod
    def formatar_tempo_decorrido(delta):
        d, h, m = delta.days, delta.seconds // 3600, (delta.seconds // 60) % 60
        if d > 0: return f"{d}d {h}h"
        if h > 0: return f"{h}h {m}m"
        return f"{m}m"
