import customtkinter as ctk

# ==========================================
# 🎨 SISTEMA DE TEMA PREMIUM (ESTÉTICA FERRARI)
# ==========================================

class Theme:
    CORES = {
        # Base
        "fundo_principal": "#1E272E",       # Mais profundo (quase black premium)
        "fundo_secundario": "#2f3640",      # Sidebar moderna
        "fundo_card": "#2d3436",            # Cards (efeito vidro escuro)

        # Vidro / Glassmorphism
        "glass": "#353d43",
        "glass_borda": "#4b5258",

        # Textos
        "texto_claro": "#f5f6fa",
        "texto_escuro": "#2f3640",
        "texto_muted": "#8395a7",

        # Destaques
        "destaque": "#00a8ff",              # Azul neon premium
        "destaque_hover": "#0097e6",

        # Status
        "sucesso": "#2ecc71",
        "alerta": "#fbc531",
        "cancelar": "#e84118",

        # Gradientes
        "gradiente_1": "#00a8ff",
        "gradiente_2": "#9c88ff"
    }

    FONTES = {
        "titulo": ("Segoe UI Variable", 28, "bold"),
        "subtitulo": ("Segoe UI", 14, "bold"),
        "corpo": ("Segoe UI", 11),
        "botao": ("Segoe UI Semibold", 12),
        "kpi": ("Segoe UI", 22, "bold")
    }

    @classmethod
    def apply_button_style(cls, button: ctk.CTkButton, style="primary"):
        """Aplica estilos pré-definidos a botões."""
        if style == "primary":
            button.configure(
                fg_color=cls.CORES["destaque"],
                hover_color=cls.CORES["destaque_hover"],
                text_color=cls.CORES["texto_claro"],
                font=cls.FONTES["botao"]
            )
        elif style == "secondary":
            button.configure(
                fg_color="transparent",
                border_width=2,
                border_color=cls.CORES["destaque"],
                text_color=cls.CORES["destaque"],
                hover_color=cls.CORES["fundo_secundario"],
                font=cls.FONTES["botao"]
            )
        elif style == "danger":
            button.configure(
                fg_color=cls.CORES["cancelar"],
                hover_color="#c0392b",
                text_color="white",
                font=cls.FONTES["botao"]
            )

    @classmethod
    def apply_input_style(cls, entry: ctk.CTkEntry):
        """Aplica estilos padrões a entradas de texto."""
        entry.configure(
            fg_color=cls.CORES["fundo_secundario"],
            border_color=cls.CORES["glass_borda"],
            border_width=1,
            text_color=cls.CORES["texto_claro"],
            placeholder_text_color=cls.CORES["texto_muted"],
            font=cls.FONTES["corpo"]
        )

# Manter compatibilidade com imports antigos
CORES = Theme.CORES
FONTES = Theme.FONTES

def configurar_estilos_ttk():
    """Configura os estilos globais para componentes do tkinter padrão (como Treeview)."""
    from tkinter import ttk
    style = ttk.Style()

    style.theme_use("default")

    # 🌑 Corpo da tabela — design moderno, mais respiro
    style.configure(
        "Treeview",
        background=Theme.CORES["fundo_card"],
        foreground=Theme.CORES["texto_claro"],
        rowheight=50,           # 🔥 Mais respiro premium (era 42)
        fieldbackground=Theme.CORES["fundo_card"],
        borderwidth=0,
        relief="flat",
        font=("Segoe UI", 11)
    )

    # 🧠 Cabeçalho estilo SaaS premium
    style.configure(
        "Treeview.Heading",
        background=Theme.CORES["fundo_secundario"],
        foreground=Theme.CORES["texto_claro"],
        font=("Segoe UI Semibold", 12),
        borderwidth=0,
        relief="flat",
        padding=(10, 10)
    )

    # 🎯 Seleção — destaque neon
    style.map(
        "Treeview",
        background=[("selected", Theme.CORES["destaque"])],
        foreground=[("selected", "#ffffff")]
    )

    # Hover no cabeçalho
    style.map(
        "Treeview.Heading",
        background=[("active", Theme.CORES["glass"])]
    )