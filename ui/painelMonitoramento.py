import tkinter as tk
from tkinter import ttk, font
import datetime
from collections import Counter
from tkinter import messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from ui.theme import CORES, FONTES
except ImportError:
    CORES = { "fundo_principal": "#f0f2f5", "fundo_barra_lateral": "#2c3e50", "fundo_card": "#ffffff", "texto_claro": "#ecf0f1", "texto_escuro": "#2c3e50", "texto_cinza": "#6c757d", "destaque_principal": "#3498db", "destaque_secundario": "#f39c12", "sucesso": "#27ae60", "alerta": "#f1c40f", "cancelar": "#e74c3c", }
    FONTES = { "titulo_dashboard": ("Arial", 18, "bold"), "subtitulo": ("Arial", 12, "bold"), "corpo": ("Arial", 10), "kpi_valor": ("Arial", 24, "bold"), "kpi_titulo": ("Arial", 10), "menu_item": ("Arial", 11), "small": ("Arial", 8), }

class PainelMonitoramento:
    """Painel de dashboard com gráficos Matplotlib funcionais, inspirado no layout moderno."""

    def __init__(self, carrinho_controller):
        self.carrinho = carrinho_controller
        self.root = tk.Toplevel()
        self.root.title("Dashboard de Monitoramento")
        self.root.geometry("1280x720")
        self.root.minsize(1100, 650)
        self.root.configure(bg=CORES.get("fundo_principal"))

        self._setup_widgets()
        self.atualizar_dashboard()

    def _setup_widgets(self):
        """Cria e organiza os widgets na janela com layout de dashboard."""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # --- BARRA LATERAL ---
        sidebar_frame = tk.Frame(self.root, bg=CORES.get("fundo_barra_lateral"), width=250)
        sidebar_frame.grid(row=0, column=0, sticky="nswe")
        sidebar_frame.pack_propagate(False)

        # Perfil do Usuário
        tk.Label(sidebar_frame, text="👤", font=("Arial", 48), bg=CORES.get("fundo_barra_lateral"), fg=CORES.get("texto_claro")).pack(pady=(20, 10))
        tk.Label(sidebar_frame, text="Admin", font=FONTES.get("subtitulo"), bg=CORES.get("fundo_barra_lateral"), fg=CORES.get("texto_claro")).pack()
        
        # O expand=True aqui é a chave para empurrar o botão de sair para baixo.
        menu_items_frame = tk.Frame(sidebar_frame, bg=CORES.get("fundo_barra_lateral"))
        menu_items_frame.pack(pady=30, fill="x", expand=True) 

        menu_items = {"Dashboard": "📊", "Inventário": "📦", "Histórico": "📄", "Usuários": "👥"}
        for text, icon in menu_items.items():
            item_frame = tk.Frame(menu_items_frame, bg=CORES.get("fundo_barra_lateral"))
            item_frame.pack(fill="x", pady=5, padx=20)
            tk.Label(item_frame, text=icon, font=FONTES.get("menu_item"), bg=CORES.get("fundo_barra_lateral"), fg=CORES.get("texto_claro")).pack(side="left", padx=10)
            tk.Label(item_frame, text=text, font=FONTES.get("menu_item"), bg=CORES.get("fundo_barra_lateral"), fg=CORES.get("texto_claro")).pack(side="left", anchor="w")
        
        # --- CÓDIGO DO BOTÃO DE SAIR ---
        btn_sair = tk.Button(
            sidebar_frame,
            text="Sair do Painel",
            command=self.root.destroy,
            bg=CORES.get("cancelar", "#e74c3c"),          
            fg=CORES.get("texto_claro", "white"),      
            font=FONTES.get("corpo", ("Arial", 10, "bold")),
            relief="flat",                               
            activebackground=CORES.get("destaque_principal"), 
            activeforeground=CORES.get("texto_claro"),
            cursor="hand2"                               
        )
        btn_sair.pack(side="bottom", fill='x', padx=20, pady=20)
        # --- ÁREA PRINCIPAL DO CONTEÚDO ---
        main_content_frame = tk.Frame(self.root, bg=CORES.get("fundo_principal"))
        main_content_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(1, weight=0); main_content_frame.grid_rowconfigure(2, weight=1); main_content_frame.grid_rowconfigure(3, weight=1)
        
        tk.Label(main_content_frame, text="Dashboard de Monitoramento de Pendências", font=FONTES.get("titulo_dashboard"), bg=CORES.get("fundo_principal"), fg=CORES.get("texto_escuro")).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # --- LINHA DOS KPIS ---
        kpis_frame = tk.Frame(main_content_frame, bg=CORES.get("fundo_principal"))
        kpis_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        for i in range(4): kpis_frame.grid_columnconfigure(i, weight=1)

        self.kpi_total_pendente = self._criar_kpi_card(kpis_frame, "Total Peças Pendentes", 0, 0)
        self.kpi_usuario_critico = self._criar_kpi_card(kpis_frame, "Usuário com Mais Pendências", 0, 1)
        self.kpi_peca_antiga = self._criar_kpi_card(kpis_frame, "Pendência Mais Antiga", 0, 2)
        self.kpi_itens_criticos = self._criar_kpi_card(kpis_frame, "Itens Críticos (>2 dias)", 0, 3)

        # --- LINHA DOS GRÁFICOS ---
        graphs_frame = tk.Frame(main_content_frame, bg=CORES.get("fundo_principal"))
        graphs_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        graphs_frame.grid_columnconfigure(0, weight=2); graphs_frame.grid_columnconfigure(1, weight=1); graphs_frame.grid_rowconfigure(0, weight=1)

        # Gráfico de Barras
        bar_chart_card = self._criar_info_card(graphs_frame, "Top 5 Peças Mais Pendentes", 0, 0)
        self.fig_bar = Figure(figsize=(5, 4), dpi=100, facecolor=CORES.get("fundo_card"))
        self.ax_bar = self.fig_bar.add_subplot(111)
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, master=bar_chart_card)
        self.canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        pie_chart_card = self._criar_info_card(graphs_frame, "Pendências por Usuário", 0, 1)
        self.fig_pie = Figure(figsize=(3, 4), dpi=100, facecolor=CORES.get("fundo_card"))
        self.ax_pie = self.fig_pie.add_subplot(111)
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, master=pie_chart_card)
        self.canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # --- TABELA DETALHADA ---
        table_card = self._criar_info_card(main_content_frame, "Detalhamento de Todas as Pendências", 3, 0)
        table_card.grid_rowconfigure(0, weight=1); table_card.grid_columnconfigure(0, weight=1)
        
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=FONTES.get("corpo"))
        style.configure("Treeview.Heading", font=FONTES.get("subtitulo"))
        
        colunas = ("usuario", "peca", "qtd", "tempo")
        self.tree = ttk.Treeview(table_card, columns=colunas, show="headings", height=5)
        self.tree.heading("usuario", text="Usuário"); self.tree.heading("peca", text="Peça"); self.tree.heading("qtd", text="Qtd."); self.tree.heading("tempo", text="Tempo")
        self.tree.column("usuario", width=200); self.tree.column("peca", width=300); self.tree.column("qtd", width=80, anchor="center"); self.tree.column("tempo", width=150, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

    def _criar_kpi_card(self, parent, titulo, row, col):
        card = tk.Frame(parent, bg=CORES.get("fundo_card"), relief="flat", bd=0)
        card.grid(row=row, column=col, sticky="nswe", padx=10, pady=5)
        tk.Label(card, text=titulo, font=FONTES.get("kpi_titulo"), bg=CORES.get("fundo_card"), fg=CORES.get("texto_cinza")).pack(anchor="n", padx=15, pady=(10, 0))
        label_valor = tk.Label(card, text="-", font=FONTES.get("kpi_valor"), bg=CORES.get("fundo_card"), fg=CORES.get("texto_escuro"), wraplength=200)
        label_valor.pack(expand=True, padx=15, pady=(0, 10))
        return label_valor

    def _criar_info_card(self, parent, titulo, row, col):
        card = tk.Frame(parent, bg=CORES.get("fundo_card"), relief="flat", bd=0)
        card.grid(row=row, column=col, sticky="nswe", padx=10, pady=5)
        card.grid_rowconfigure(1, weight=1); card.grid_columnconfigure(0, weight=1)
        tk.Label(card, text=titulo, font=FONTES.get("subtitulo"), bg=CORES.get("fundo_card"), fg=CORES.get("texto_escuro")).grid(row=0, column=0, sticky="nw", padx=15, pady=10)
        content = tk.Frame(card, bg=CORES.get("fundo_card"))
        content.grid(row=1, column=0, sticky="nswe", padx=10, pady=5)
        return content

    def _desenhar_grafico_barras(self, dados):
        self.ax_bar.clear()
        if not dados:
            self.ax_bar.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        else:
            pecas = [p[:25] + '...' if len(p) > 25 else p for p in dados.keys()]
            quantidades = list(dados.values())
            self.ax_bar.barh(pecas, quantidades, color=CORES.get("destaque_principal"))
            self.ax_bar.invert_yaxis()
            self.ax_bar.tick_params(axis='both', which='major', labelsize=8)
        self.fig_bar.tight_layout(pad=1.5)
        self.canvas_bar.draw()
        
    def _desenhar_grafico_pizza(self, dados):
        self.ax_pie.clear()
        if not dados:
            self.ax_pie.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        else:
            labels = list(dados.keys())
            sizes = list(dados.values())
            cores = [CORES.get("destaque_principal"), CORES.get("destaque_secundario", "#f39c12"), CORES.get("texto_cinza")]
            
            wedges, texts, autotexts = self.ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                                                       wedgeprops=dict(width=0.4), colors=cores[:len(labels)],
                                                       textprops={'fontsize': 9, 'color': CORES.get("texto_escuro")})
            for autotext in autotexts: autotext.set_color('white')

        self.fig_pie.tight_layout(pad=1.5)
        self.canvas_pie.draw()

    def atualizar_dashboard(self):
        try:
            for item in self.tree.get_children(): self.tree.delete(item)
            
            pendencias = [p for p in self.carrinho.db.obter_todas_retiradas_pendentes() if (p.quantidade_retirada - p.quantidade_devolvida) > 0]
            
            total_pecas = 0; usuarios_counter = Counter(); pecas_counter = Counter()
            peca_antiga = {"nome": "Nenhuma", "tempo_str": "-"}; max_delta = datetime.timedelta(0)
            itens_criticos = 0

            for ret in pendencias:
                usuario = self.carrinho.db.obter_usuario_por_id(ret.usuario_id)
                peca = self.carrinho.db.obter_peca_por_id(ret.peca_id)
                nome_usuario = usuario.nome if usuario else f"ID {ret.usuario_id}"
                nome_peca = peca.nome if peca else f"ID {ret.peca_id}"
                qtd = ret.quantidade_retirada - ret.quantidade_devolvida
                
                total_pecas += qtd
                usuarios_counter[nome_usuario] += qtd
                pecas_counter[nome_peca] += qtd
                
                ts = datetime.datetime.fromisoformat(ret.timestamp_retirada)
                delta = datetime.datetime.now() - ts
                
                if delta.days >= 2: itens_criticos += qtd
                if delta > max_delta: max_delta, peca_antiga = delta, {"nome": nome_peca, "tempo_str": self.formatar_tempo_decorrido(delta)}
                self.tree.insert("", "end", values=(nome_usuario, nome_peca, qtd, self.formatar_tempo_decorrido(delta)))

            self.kpi_total_pendente.config(text=str(total_pecas))
            if usuarios_counter:
                user_critico, count = usuarios_counter.most_common(1)[0]
                self.kpi_usuario_critico.config(text=f"{user_critico}\n({count} itens)")
            else: self.kpi_usuario_critico.config(text="Nenhum")
            self.kpi_peca_antiga.config(text=f"{peca_antiga['nome']}\n({peca_antiga['tempo_str']})")
            self.kpi_itens_criticos.config(text=str(itens_criticos))
            
            # --- ATUALIZA GRÁFICOS ---
            self._desenhar_grafico_barras(dict(pecas_counter.most_common(5)))
            self._desenhar_grafico_pizza(dict(usuarios_counter.most_common(3)))

        except Exception as e:
            print(f"ERRO ao atualizar dashboard: {e}")
            messagebox.showerror("Erro de Atualização", f"Não foi possível carregar os dados: {e}")

        self.root.after(60000, self.atualizar_dashboard)

    @staticmethod
    def formatar_tempo_decorrido(delta):
        d, h, m = delta.days, delta.seconds // 3600, (delta.seconds // 60) % 60
        if d > 0: return f"{d}d {h}h"
        if h > 0: return f"{h}h {m}min"
        return f"{m}min"

# --- Bloco de Teste ---
if __name__ == '__main__':
    class MockRetirada:
        def __init__(self, uid, pid, ts, qr, qd): self.usuario_id, self.peca_id, self.timestamp_retirada, self.quantidade_retirada, self.quantidade_devolvida = uid, pid, ts, qr, qd
    class MockUsuario:
        def __init__(self, nome): self.nome = nome
    class MockPeca:
        def __init__(self, nome): self.nome = nome
    class MockDB:
        def obter_todas_retiradas_pendentes(self):
            now = datetime.datetime.now()
            return [MockRetirada(1, 101, (now - datetime.timedelta(minutes=30)).isoformat(), 1, 0), MockRetirada(2, 102, (now - datetime.timedelta(hours=9)).isoformat(), 5, 2), MockRetirada(1, 103, (now - datetime.timedelta(days=3, hours=4)).isoformat(), 1, 0), MockRetirada(3, 104, (now - datetime.timedelta(days=1)).isoformat(), 2, 1), MockRetirada(2, 105, (now - datetime.timedelta(hours=1)).isoformat(), 1, 0), MockRetirada(1, 102, (now - datetime.timedelta(hours=5)).isoformat(), 3, 0), MockRetirada(4, 102, (now - datetime.timedelta(hours=2)).isoformat(), 2, 0)]
        def obter_usuario_por_id(self, uid): return MockUsuario({1: "Ana Beatriz", 2: "Carlos Eduardo", 3: "Daniela Costa", 4: "Fábio Lima"}.get(uid, "Desconhecido"))
        def obter_peca_por_id(self, pid): return MockPeca({101: "Chave Phillips #2", 102: "Parafuso Sextavado M6 x 20mm", 103: "Alicate de Bico Fino Profissional", 104: "Martelo de Borracha", 105: "Fita Isolante 10m"}.get(pid, "Peça Desconhecida"))
    class MockCarrinhoController:
        def __init__(self): self.db = MockDB()
    root_app = tk.Tk()
    root_app.withdraw()
    painel = PainelMonitoramento(MockCarrinhoController())
    root_app.mainloop()