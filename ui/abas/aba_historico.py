import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from ui.theme import CORES, FONTES

class AbaHistorico(ttk.Frame):
    """Frame que exibe o histórico de eventos do sistema."""
    def __init__(self, parent, carrinho_controller, app_controller):
        super().__init__(parent)
        self.carrinho = carrinho_controller
        self.app = app_controller

        self.setup_widgets()
        self.atualizar_historico()

    def setup_widgets(self):
        style = ttk.Style()
        style.configure("Sucesso.TButton",
                        font=FONTES["botao"],
                        background=CORES["sucesso"],
                        foreground=CORES["texto_claro"])
        style.map("Sucesso.TButton",
                  background=[('active', '#27ae60')]) 
        cor_vermelha = CORES.get("cancelar", "#e74c3c")
        cor_vermelha_active = CORES.get("cancelar_active", "#c0392b")
        style.configure("Remover.TButton",
                        font=FONTES["botao"],
                        background=cor_vermelha,
                        foreground=CORES["texto_claro"])
        style.map("Remover.TButton",
                  background=[('active', cor_vermelha_active)])

        frame_historico = ttk.LabelFrame(self, text="Histórico de Eventos", padding=10)
        frame_historico.pack(fill='both', expand=True, padx=10, pady=5)

        columns_hist = ('Data/Hora', 'Gaveta', 'Usuário', 'Ação', 'Status')
        self.tree_historico = ttk.Treeview(frame_historico, columns=columns_hist, show='headings', height=15)
        for col in columns_hist:
            self.tree_historico.heading(col, text=col)
            self.tree_historico.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame_historico, orient='vertical', command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar.set)
        self.tree_historico.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=10)

        ttk.Button(
            frame_botoes, 
            text="Atualizar Histórico", 
            command=self.atualizar_historico,
            style="Sucesso.TButton"
        ).pack(side='left', padx=10)

        ttk.Button(
            frame_botoes, 
            text="Apagar Histórico", 
            command=self.apagar_historico,
            style="Remover.TButton"
        ).pack(side='left', padx=10)

    def atualizar_historico(self):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        
        eventos = self.carrinho.db.obter_historico(100)
        for evento in eventos:
            timestamp = evento.timestamp
            try:
                timestamp = datetime.datetime.fromisoformat(timestamp).strftime("%d/%m/%Y %H:%M:%S")
            except (ValueError, AttributeError):
                pass
            
            status = "✓ Sucesso" if evento.sucesso else "✗ Falha"
            usuario = self.carrinho.db.obter_usuario(evento.usuario_id)
            nome_usuario = usuario.nome if usuario else evento.usuario_id
            self.tree_historico.insert('', 'end', values=(
                timestamp, f"Gaveta {evento.gaveta_id}", nome_usuario, evento.acao.capitalize(), status
            ))

    def apagar_historico(self):
        """Apaga todos os registros da tabela de histórico."""
        confirmar = messagebox.askyesno(
            "Confirmar Exclusão", 
            "Tem certeza que deseja apagar TODO o histórico de eventos?\nEsta ação não pode ser desfeita.",
            icon='warning'
        )
        
        if confirmar:
            try:
                self.carrinho.db.limpar_historico()
                messagebox.showinfo("Sucesso", "Histórico de eventos foi apagado com sucesso!")
                self.atualizar_historico() 
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível apagar o histórico: {e}")