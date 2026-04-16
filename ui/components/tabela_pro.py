import customtkinter as ctk
from ui.theme import CORES, FONTES

# ──────────────────────────────────────────────
#  🚀 TabelaPRO — Tabela custom 100% CTkinter
#     Sem ttk.Treeview | Hover real | Badges | Tooltip
# ──────────────────────────────────────────────

# Paleta interna (depth)
_EVEN_BG   = "#262c31"
_ODD_BG    = "#2f363c"
_HOVER_BG  = "#394149"
_HEADER_BG = "#2f3640"
_DIVIDER   = "#4b5258"

# Mapa de cores para badges de status
STATUS_CORES = {
    "PENDENTE":  ("#fbc531", "#1a1200"),   # amarelo
    "DEVOLVIDO": ("#2ecc71", "#0a1f0f"),   # verde
    "sucesso":   ("#2ecc71", "#0a1f0f"),
    "falha":     ("#e84118", "#200000"),
    "default":   ("#8395a7", "#1a1f24"),
}


def _badge(parent: ctk.CTkFrame, texto: str) -> ctk.CTkLabel:
    """Cria um badge colorido baseado no texto do status (Pílula suave)."""
    key = texto.upper() if texto.upper() in STATUS_CORES else "default"
    bg, fg = STATUS_CORES.get(key, ("#8395a7", "#1a1f24"))
    
    badge = ctk.CTkLabel(
        parent,
        text=texto,
        fg_color=bg,
        text_color=fg,
        corner_radius=12,  # Borda perfeitamente arredondada sem pontas
        font=("Segoe UI Semibold", 11),
        padx=12, pady=4,
    )
    return badge


class TabelaPRO(ctk.CTkFrame):
    """
    Tabela customizada 100% CTkinter.

    Parâmetros
    ----------
    parent      : widget pai
    columns     : lista de str com nomes das colunas
    col_widths  : lista de int (opcional) com larguras relativas por coluna.
                  Se omitido, todas as colunas terão peso 1.
    status_col  : índice da coluna que renderiza como badge (ou None)
    on_select   : callback(row_data: list) ao clicar em uma linha
    on_edit     : callback(row_data: list) ao clicar em ✏  — se None, botão oculto
    on_delete   : callback(row_data: list) ao clicar em 🗑  — se None, botão oculto
    show_actions: bool — exibe coluna de ações (padrão True)
    """

    def __init__(
        self,
        parent,
        columns: list,
        col_widths: list | None = None,
        status_col: int | None = None,
        on_select=None,
        on_edit=None,
        on_delete=None,
        show_actions: bool = True,
    ):
        super().__init__(parent, fg_color="transparent")

        self.columns     = columns
        self.col_widths  = col_widths or [1] * len(columns)
        self.status_col  = status_col
        self.on_select   = on_select
        self.on_edit     = on_edit
        self.on_delete   = on_delete
        self.show_actions = show_actions and (on_edit is not None or on_delete is not None)

        self._rows: list[ctk.CTkFrame] = []   # referências a cada frame de linha
        self._data: list[list]         = []   # dados brutos de cada linha
        self._selected_index: int | None = None
        self._tooltip_win              = None

        self._build_header()
        self._divider()

        # Área de scroll para as linhas
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True)
        self._configure_grid(self._scroll)

    # ── Construção ────────────────────────────────────────

    def _configure_grid(self, frame: ctk.CTkFrame):
        """Configura pesos das colunas no frame."""
        for i, w in enumerate(self.col_widths):
            frame.columnconfigure(i, weight=w)
        if self.show_actions:
            frame.columnconfigure(len(self.columns), weight=0, minsize=80)

    def _build_header(self):
        """Constrói o cabeçalho fixo."""
        self._header = ctk.CTkFrame(self, fg_color=_HEADER_BG, corner_radius=10)
        self._header.pack(fill="x", padx=0, pady=(0, 0))
        self._configure_grid(self._header)

        for i, col in enumerate(self.columns):
            ctk.CTkLabel(
                self._header,
                text=col,
                font=("Segoe UI Semibold", 12),
                text_color=CORES["texto_claro"],
                anchor="w",
            ).grid(row=0, column=i, padx=14, pady=12, sticky="w")

        if self.show_actions:
            ctk.CTkLabel(
                self._header,
                text="Ações",
                font=("Segoe UI Semibold", 12),
                text_color=CORES["texto_muted"],
                anchor="center",
            ).grid(row=0, column=len(self.columns), padx=10, pady=12)

    def _divider(self):
        """Linha separadora sutil abaixo do cabeçalho."""
        ctk.CTkFrame(self, height=1, fg_color=_DIVIDER).pack(fill="x")

    # ── API pública ───────────────────────────────────────

    def carregar(self, data: list[list]):
        """
        Carrega (ou recarrega) a tabela com novos dados.
        `data` é uma lista de linhas, cada linha é uma lista de valores.
        """
        self.limpar()
        self._data = list(data)
        for i, row_data in enumerate(self._data):
            self._add_row(i, row_data)

    def limpar(self):
        """Remove todas as linhas da tabela."""
        for f in self._rows:
            f.destroy()
        self._rows.clear()
        self._data.clear()
        self._selected_index = None

    # ── Renderização de linhas ────────────────────────────

    def _add_row(self, index: int, row_data: list):
        base_color  = _EVEN_BG if index % 2 == 0 else _ODD_BG
        radius      = 8

        row_frame = ctk.CTkFrame(
            self._scroll,
            fg_color=base_color,
            corner_radius=radius,
        )
        row_frame.pack(fill="x", padx=0, pady=2)
        self._configure_grid(row_frame)

        # ── hover ──
        def _enter(e, f=row_frame, idx=index):
            if idx != self._selected_index:
                f.configure(fg_color=_HOVER_BG)

        def _leave(e, f=row_frame, idx=index, bg=base_color):
            if idx != self._selected_index:
                f.configure(fg_color=bg)

        def _click(e, idx=index, rd=row_data):
            self._set_selected(idx)
            if self.on_select:
                self.on_select(rd)

        row_frame.bind("<Enter>", _enter)
        row_frame.bind("<Leave>", _leave)
        row_frame.bind("<Button-1>", _click)

        # ── células ──
        for col_i, value in enumerate(row_data):
            is_status = (col_i == self.status_col)

            if is_status:
                cell = _badge(row_frame, str(value))
                cell.grid(row=0, column=col_i, padx=10, pady=8, sticky="w")
                cell.bind("<Button-1>", _click)
                cell.bind("<Enter>",    _enter)
                cell.bind("<Leave>",    _leave)
            else:
                lbl = ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    font=FONTES["corpo"],
                    text_color=CORES["texto_claro"],
                    anchor="w",
                )
                lbl.grid(row=0, column=col_i, padx=14, pady=14, sticky="w")
                lbl.bind("<Button-1>", _click)
                lbl.bind("<Enter>",    _enter)
                lbl.bind("<Leave>",    _leave)

                # Tooltip na primeira coluna de texto (coluna 1 geralmente é Nome)
                if col_i == 1:
                    lbl.bind("<Enter>", lambda e, v=str(value), f=row_frame, idx=index: (
                        _enter(e),
                        self._show_tooltip(e, v)
                    ))
                    lbl.bind("<Leave>", lambda e, f=row_frame, idx=index, bg=base_color: (
                        _leave(e),
                        self._hide_tooltip()
                    ))

        # ── botões de ação ──
        if self.show_actions:
            btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=len(row_data), padx=8, pady=6)

            if self.on_edit:
                ctk.CTkButton(
                    btn_frame,
                    text="✏",
                    width=32, height=32,
                    font=("Segoe UI", 13),
                    fg_color=CORES["destaque"],
                    hover_color=CORES["destaque_hover"],
                    corner_radius=8,
                    command=lambda rd=row_data: self.on_edit(rd),
                ).pack(side="left", padx=3)

            if self.on_delete:
                ctk.CTkButton(
                    btn_frame,
                    text="🗑",
                    width=32, height=32,
                    font=("Segoe UI", 13),
                    fg_color=CORES["cancelar"],
                    hover_color="#c0392b",
                    corner_radius=8,
                    command=lambda rd=row_data: self.on_delete(rd),
                ).pack(side="left", padx=3)

        self._rows.append(row_frame)

    def _set_selected(self, index: int):
        """Marca visualmente a linha selecionada."""
        # Deseleciona anterior
        if self._selected_index is not None and self._selected_index < len(self._rows):
            prev_bg = _EVEN_BG if self._selected_index % 2 == 0 else _ODD_BG
            self._rows[self._selected_index].configure(fg_color=prev_bg)

        self._selected_index = index
        if index < len(self._rows):
            self._rows[index].configure(fg_color=CORES["destaque"])

    # ── Tooltip ───────────────────────────────────────────
    def _init_tooltip(self):
        if not getattr(self, "_tooltip_win", None):
            self._tooltip_win = ctk.CTkToplevel(self)
            self._tooltip_win.overrideredirect(True)
            self._tooltip_win.attributes("-topmost", True)
            self._tooltip_win.withdraw()
            self._tooltip_label = ctk.CTkLabel(
                self._tooltip_win,
                text="",
                fg_color=CORES["fundo_secundario"],
                text_color=CORES["texto_claro"],
                corner_radius=6,
                padx=12, pady=6,
                font=FONTES["corpo"],
            )
            self._tooltip_label.pack()
            # Oculta se a aba for escondida
            self.bind("<Unmap>", lambda e: self._hide_tooltip(), add="+")

    def _show_tooltip(self, event, texto: str):
        self._init_tooltip()
        self._tooltip_label.configure(text=texto)
        self._tooltip_win.geometry(f"+{event.x_root + 14}+{event.y_root + 14}")
        self._tooltip_win.deiconify()

    def _hide_tooltip(self):
        if getattr(self, "_tooltip_win", None):
            self._tooltip_win.withdraw()
