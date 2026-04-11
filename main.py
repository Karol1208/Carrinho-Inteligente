import datetime
import logging
import sys
import os
# Suas importações originais
from core.cart import CarrinhoInteligenteAvancado
from ui.login import TelaLogin
from models.entities import UsuarioCartao
from ui.interface import InterfaceGraficaCarrinho
from utils.config import setup_logging

# --- Seção de Configuração do Hardware ---
MODO_HARDWARE = "real"  # Mude para "simulador" para testar sem o Arduino
PORTA_SERIAL = None     # Deixe None para detecção automática
# -----------------------------------------

def inicializar_sistema_exemplo(db_path: str = 'carrinho.db') -> CarrinhoInteligenteAvancado:
    setup_logging()
    
    if MODO_HARDWARE == "real":
        carrinho = CarrinhoInteligenteAvancado(db_path=db_path, modo_hardware='real', porta_serial=PORTA_SERIAL)
    else:
        carrinho = CarrinhoInteligenteAvancado(db_path=db_path, modo_hardware='simulador')

    # Adiciona usuários de exemplo (lógica do seu colega mantida)
    usuarios_exemplo = [
        UsuarioCartao(id="1234", nome="João Silva", cargo="Professor", perfil="admin", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="6789", nome="Maria Santos", cargo="Supervisora", perfil="admin", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="1111", nome="Pedro Costa", cargo="Líder", perfil="aluno", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="2222", nome="Ana Lima", cargo="Aluno", perfil="aluno", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
    ]
    for usuario in usuarios_exemplo:
        carrinho.db.adicionar_usuario(usuario)

    logging.info("Sistema inicializado com usuários de exemplo.")
    return carrinho

def carregar_branding(root):
    """Configura o ícone da janela."""
    try:
        # Tenta carregar o ícone (.ico no windows, .png em outros)
        if sys.platform.startswith('win'):
            if os.path.exists("assets/favicon.ico"):
                root.iconbitmap("assets/favicon.ico")
        else:
            from tkinter import PhotoImage
            if os.path.exists("assets/logo.png"):
                img = PhotoImage(file="assets/logo.png")
                root.iconphoto(True, img)
    except Exception as e:
        logging.warning(f"Não foi possível carregar o ícone: {e}")

# Versão NOVA e CORRIGIDA
if __name__ == "__main__":
    from ui.theme import configurar_estilos_ttk
    
    # Inicia um loop infinito para o sistema
    while True:
        carrinho = inicializar_sistema_exemplo()
        
        tela_login = TelaLogin(carrinho)
        configurar_estilos_ttk() # Carrega estilos TTK (Treeview)
        carregar_branding(tela_login.root)
        
        usuario, perfil = tela_login.executar()
        
        if usuario:
            # Se o login for bem-sucedido, abre a interface principal
            interface = InterfaceGraficaCarrinho(carrinho=carrinho, usuario_inicial=usuario)
            carregar_branding(interface.root)
            interface.executar()
            # Quando a interface.executar() terminar (janela fechada), o loop recomeça
        else:
            # Se o usuário fechar a tela de login sem logar, o loop é quebrado e o programa fecha.
            logging.info("Nenhum usuário autenticado. Encerrando o sistema.")
            if carrinho and hasattr(carrinho.hardware, 'close'):
                carrinho.hardware.close()
            break # Sai do loop while True