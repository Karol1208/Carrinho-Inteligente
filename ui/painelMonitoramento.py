import tkinter as tk
from tkinter import ttk
import datetime

class PainelMonitoramento:
    """Painel que monitora e exibe todas as peças com devolução pendente."""
    def __init__(self, carrinho):
        self.carrinho = carrinho
        self.root = tk.Toplevel()
        self.root.title("Painel de Monitoramento de Peças Pendentes")
        self.root.geometry("800x400") 
        self.root.minsize(700, 300)

        self.tree = ttk.Treeview(self.root, columns=("usuario", "peca", "qtd_pendente", "data_retirada", "tempo_decorrido"), show="headings")
        self.tree.heading("usuario", text="Usuário")
        self.tree.heading("peca", text="Peça Não Devolvida")
        self.tree.heading("qtd_pendente", text="Qtd. Pendente")
        self.tree.heading("data_retirada", text="Data da Retirada")
        self.tree.heading("tempo_decorrido", text="Tempo Decorrido")

        self.tree.column("usuario", width=150)
        self.tree.column("peca", width=200)
        self.tree.column("qtd_pendente", width=100, anchor="center")
        self.tree.column("data_retirada", width=150, anchor="center")
        self.tree.column("tempo_decorrido", width=150, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_fechar = ttk.Button(self.root, text="Fechar Painel", command=self.root.destroy)
        btn_fechar.pack(pady=5)

        self.atualizar_pendencias()

    def atualizar_pendencias(self):
        """Busca todas as peças pendentes e atualiza a lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        pendencias = self.carrinho.db.obter_todas_retiradas_pendentes()

        for retirada in pendencias:
            usuario = self.carrinho.db.obter_usuario_por_id(retirada.usuario_id)
            peca = self.carrinho.db.obter_peca_por_id(retirada.peca_id)
            
            nome_usuario = usuario.nome if usuario else "ID " + retirada.usuario_id
            nome_peca = peca.nome if peca else "ID " + str(retirada.peca_id)
            
            qtd_pendente = retirada.quantidade_retirada - retirada.quantidade_devolvida
            
            try:
                timestamp_retirada = datetime.datetime.fromisoformat(retirada.timestamp_retirada)
                data_formatada = timestamp_retirada.strftime("%d/%m/%Y %H:%M")
                tempo_decorrido = datetime.datetime.now() - timestamp_retirada
                tempo_str = self.formatar_tempo_decorrido(tempo_decorrido)
            except (ValueError, TypeError):
                data_formatada = "Data inválida"
                tempo_str = "N/A"

            self.tree.insert("", "end", values=(nome_usuario, nome_peca, qtd_pendente, data_formatada, tempo_str))

        self.root.after(30000, self.atualizar_pendencias)

    @staticmethod
    def formatar_tempo_decorrido(delta: datetime.timedelta):
        """Formata um objeto timedelta em uma string legível (dias, horas, minutos)."""
        dias = delta.days
        horas, rem = divmod(delta.seconds, 3600)
        minutos, _ = divmod(rem, 60)

        if dias > 0:
            return f"{dias}d {horas}h"
        elif horas > 0:
            return f"{horas}h {minutos}min"
        else:
            return f"{minutos}min"