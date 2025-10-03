import tkinter as tk
from tkinter import ttk
import datetime

class PainelMonitoramento:
    def __init__(self, carrinho):
        self.carrinho = carrinho
        self.root = tk.Toplevel()
        self.root.title("Painel de Monitoramento de Gavetas")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self.tree = ttk.Treeview(self.root, columns=("gaveta", "usuario", "tempo_aberta"), show="headings")
        self.tree.heading("gaveta", text="Gaveta")
        self.tree.heading("usuario", text="Usuário")
        self.tree.heading("tempo_aberta", text="Tempo Aberta")
        self.tree.column("gaveta", width=80, anchor="center")
        self.tree.column("usuario", width=250)
        self.tree.column("tempo_aberta", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_fechar = ttk.Button(self.root, text="Fechar Painel", command=self.root.destroy)
        btn_fechar.pack(pady=5)

        self.atualizar_alertas()

    def atualizar_alertas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Verifica gavetas abertas há mais de 10 minutos
        for gaveta_id, gaveta in self.carrinho.gavetas.items():
            if gaveta.aberta:
                tempo_aberta = gaveta.tempo_aberta()
                if tempo_aberta >= 600:  # 10 minutos
                    usuario = self.carrinho.db.obter_usuario(gaveta.usuario_atual) if hasattr(gaveta, 'usuario_atual') and gaveta.usuario_atual else None
                    nome_usuario = usuario.nome if usuario else "Desconhecido"
                    tempo_str = self.formatar_tempo(tempo_aberta)
                    self.tree.insert("", "end", values=(f"Gaveta {gaveta_id}", nome_usuario, tempo_str))

        # Atualiza a cada 10 segundos
        self.root.after(10000, self.atualizar_alertas)

    @staticmethod
    def formatar_tempo(segundos):
        minutos = int(segundos // 60)
        segundos_rest = int(segundos % 60)
        return f"{minutos} min {segundos_rest} s"