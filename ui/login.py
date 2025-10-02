import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
from core.cart import CarrinhoInteligenteAvancado

class TelaLogin:
    def __init__(self, carrinho: CarrinhoInteligenteAvancado):
        self.carrinho = carrinho
        self.usuario = None
        self.perfil = None

        self.root = tk.Tk()
        self.root.title("Login - CRDF")
        self.root.geometry("400x300")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)

        # Fonte estilizada para a sigla
        self.fonte_sigla = tkFont.Font(family="Helvetica", size=48, weight="bold")
        self.fonte_label = tkFont.Font(family="Arial", size=12)
        self.fonte_entrada = tkFont.Font(family="Arial", size=14)

        self.setup_interface()

    def setup_interface(self):
        # Sigla CRDF no topo
        label_sigla = tk.Label(self.root, text="CRDF", font=self.fonte_sigla, fg="#ecf0f1", bg="#2c3e50")
        label_sigla.pack(pady=(30, 10))

        # Label instrução
        label_instrucao = tk.Label(self.root, text="Digite o código do cartão para login", font=self.fonte_label, fg="#bdc3c7", bg="#2c3e50")
        label_instrucao.pack(pady=(0, 20))

        # Entrada do código do cartão
        self.entry_codigo = ttk.Entry(self.root, font=self.fonte_entrada, justify="center")
        self.entry_codigo.pack(ipady=5, ipadx=10)
        self.entry_codigo.focus()
        self.entry_codigo.bind("<Return>", self.validar_login)

        # Botão de login
        btn_login = ttk.Button(self.root, text="Entrar", command=self.validar_login)
        btn_login.pack(pady=20)

    def validar_login(self, event=None):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Por favor, digite o código do cartão.")
            return

        usuario = self.carrinho.validar_cartao(codigo)
        if usuario:
            self.usuario = usuario
            self.perfil = usuario.perfil
            messagebox.showinfo("Bem-vindo", f"Olá, {usuario.nome}!\nPerfil: {usuario.perfil}")
            self.root.destroy()
        else:
            messagebox.showerror("Erro", "Cartão não autorizado ou inválido.")
            self.entry_codigo.delete(0, tk.END)

    def executar(self):
        self.root.mainloop()
        return self.usuario, self.perfil

# Exemplo de uso:
if __name__ == "__main__":
    from core.cart import CarrinhoInteligenteAvancado
    carrinho = CarrinhoInteligenteAvancado()
    tela_login = TelaLogin(carrinho)
    usuario, perfil = tela_login.executar()
    if usuario:
        print(f"Usuário logado: {usuario.nome} - Perfil: {perfil}")
        # Aqui você pode abrir a interface principal já configurada para o perfil do usuário
    else:
        print("Login cancelado ou falhou.")