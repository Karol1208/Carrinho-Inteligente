import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime
from collections import Counter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import CORES, FONTES
from ui.components.glass_card import GlassCard

class PainelMonitoramento:
    """Painel de dashboard com gráficos Matplotlib funcionais, inspirado no layout moderno."""

    def __init__(self, carrinho_controller):
        self.carrinho = carrinho_controller
        self.root = ctk.CTkToplevel()
        self.root.title("Dashboard de Monitoramento Premium")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 750)
        self.root.configure(fg_color=CORES["fundo_principal"])
        
        ctk.set_appearance_mode("dark")

        self._setup_widgets()
        self.atualizar_dashboard()

    def _setup_widgets(self):
        """Cria e organiza os widgets na janela com layout de dashboard premium."""
        
        # 1. Header do Dashboard
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(side="top", fill="x", padx=30, pady=(30, 10))
        
        ctk.CTkLabel(
            header_frame, 
            text="Dashboard de Peças Pendentes", 
            font=("Segoe UI Variable", 32, "bold"),
            text_color=CORES["texto_claro"]
        ).pack(side="left")

        ctk.CTkButton(
            header_frame,
            text="Fechar Painel",
            width=120,
            fg_color=CORES["cancelar"],
            hover_color="#c0392b",
            command=self.root.destroy
        ).pack(side="right")

        # 2. Scrollable Container para o Conteúdo
        self.main_scroll = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # 3. LINHA DOS KPIS (Cards Superiores)
        kpi_row = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        kpi_row.pack(fill="x", pady=10)

        self.kpi_total = self._criar_kpi_card(kpi_row, "Total Pendente", "📦")
        self.kpi_critico = self._criar_kpi_card(kpi_row, "Usuário Crítico", "⚠️")
        self.kpi_antigo = self._criar_kpi_card(kpi_row, "Item Mais Antigo", "⏳")
        self.kpi_alerta = self._criar_kpi_card(kpi_row, "Atraso > 2 Dias", "🚨")

        # 4. LINHA DOS GRÁFICOS
        charts_row = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        charts_row.pack(fill="x", pady=10)

        # Card Gráfico de Barras
        bar_card = GlassCard(charts_row)
        bar_card.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(bar_card, text="Top 5 Peças Mais Pendentes", font=FONTES["subtitulo"]).pack(pady=10)
        
        self.fig_bar = Figure(figsize=(5, 4), dpi=100, facecolor=CORES["fundo_card"])
        self.ax_bar = self.fig_bar.add_subplot(111)
        self.ax_bar.set_facecolor(CORES["fundo_card"])
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, master=bar_card)
        self.canvas_bar.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

        # Card Gráfico de Pizza
        pie_card = GlassCard(charts_row)
        pie_card.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(pie_card, text="Distribuição por Usuário", font=FONTES["subtitulo"]).pack(pady=10)
        
        self.fig_pie = Figure(figsize=(4, 4), dpi=100, facecolor=CORES["fundo_card"])
        self.ax_pie = self.fig_pie.add_subplot(111)
        self.ax_pie.set_facecolor(CORES["fundo_card"])
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, master=pie_card)
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

        # 5. TABELA DETALHADA
        table_card = GlassCard(self.main_scroll)
        table_card.pack(fill="both", expand=True, padx=10, pady=20)
        ctk.CTkLabel(table_card, text="Detalhamento das Pendências em Tempo Real", font=FONTES["subtitulo"]).pack(pady=10)

        # Configuração Treeview (Estilo Moderno via ttk)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background=CORES["fundo_card"], 
                        foreground=CORES["texto_claro"], 
                        fieldbackground=CORES["fundo_card"],
                        rowheight=35,
                        font=FONTES["corpo"])
        style.configure("Treeview.Heading", 
                        background=CORES["fundo_secundario"], 
                        foreground=CORES["texto_claro"],
                        font=FONTES["botao"])
        style.map("Treeview", background=[('selected', CORES["destaque"])])

        cols = ("usuario", "peca", "qtd", "tempo")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings")
        self.tree.heading("usuario", text="Usuário"); self.tree.heading("peca", text="Chave / Ferramenta")
        self.tree.heading("qtd", text="Qtd."); self.tree.heading("tempo", text="Tempo Decorrido")
        
        self.tree.column("usuario", width=250); self.tree.column("peca", width=350)
        self.tree.column("qtd", width=100, anchor="center"); self.tree.column("tempo", width=200, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def _criar_kpi_card(self, parent, titulo, icone):
        card = GlassCard(parent)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        ctk.CTkLabel(card, text=f"{icone} {titulo}", font=FONTES["corpo"], text_color=CORES["texto_muted"]).pack(pady=(15, 5))
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
            pecas = [p[:20] + '...' if len(p) > 20 else p for p in dados.keys()]
            quantidades = list(dados.values())
            self.ax_bar.barh(pecas, quantidades, color=CORES["destaque"])
            self.ax_bar.invert_yaxis()
        
        self.fig_bar.tight_layout()
        self.canvas_bar.draw()
        
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
        self.canvas_pie.draw()

    def atualizar_dashboard(self):
        if not self.root.winfo_exists(): return
        
        try:
            for item in self.tree.get_children(): self.tree.delete(item)
            pendencias = [p for p in self.carrinho.db.obter_todas_retiradas_pendentes() if (p.quantidade_retirada - p.quantidade_devolvida) > 0]
            
            total_pecas = 0; usuarios_counter = Counter(); pecas_counter = Counter()
            peca_antiga = "Nenhuma"; itens_criticos = 0; max_delta = datetime.timedelta(0)

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
                
                self.tree.insert("", "end", values=(nome_u, nome_p, qtd, self.formatar_tempo_decorrido(delta)))

            self.kpi_total.configure(text=str(total_pecas))
            self.kpi_critico.configure(text=usuarios_counter.most_common(1)[0][0] if usuarios_counter else "Nenhum")
            self.kpi_antigo.configure(text=peca_antiga)
            self.kpi_alerta.configure(text=str(itens_criticos), text_color=CORES["cancelar"] if itens_criticos > 0 else CORES["destaque"])
            
            self._desenhar_grafico_barras(dict(pecas_counter.most_common(5)))
            self._desenhar_grafico_pizza(dict(usuarios_counter.most_common(3)))

        except Exception as e:
            print(f"ERRO Dashboard: {e}")

        self.root.after(30000, self.atualizar_dashboard)

    @staticmethod
    def formatar_tempo_decorrido(delta):
        d, h, m = delta.days, delta.seconds // 3600, (delta.seconds // 60) % 60
        if d > 0: return f"{d}d {h}h"
        if h > 0: return f"{h}h {m}m"
        return f"{m}m"