import datetime
import logging

from core.cart import CarrinhoInteligenteAvancado
from models.entities import UsuarioCartao
from ui.interface import InterfaceGraficaCarrinho
from utils.config import setup_logging

# Importa a tela de login criada
from ui.login import TelaLogin  # Ajuste o caminho conforme seu projeto


def inicializar_sistema_exemplo(db_path: str = 'carrinho.db') -> CarrinhoInteligenteAvancado:
    setup_logging()
    carrinho = CarrinhoInteligenteAvancado(db_path=db_path)

    usuarios_exemplo = [
        UsuarioCartao("12345", "João Silva", "Professor", perfil="admin", data_cadastro=datetime.datetime.now().isoformat()),
        UsuarioCartao("67890", "Maria Santos", "Supervisora", perfil="admin", data_cadastro=datetime.datetime.now().isoformat()),
        UsuarioCartao("11111", "Pedro Costa", "Líder", perfil="aluno", data_cadastro=datetime.datetime.now().isoformat()),
        UsuarioCartao("22222", "Ana Lima", "Aluno", perfil="aluno", data_cadastro=datetime.datetime.now().isoformat()),
    ]
    for usuario in usuarios_exemplo:
        carrinho.db.adicionar_usuario(usuario)

    logging.info("Sistema inicializado com usuários de exemplo.")
    return carrinho


if __name__ == "__main__":
    carrinho = inicializar_sistema_exemplo()

    # Abre a tela de login
    tela_login = TelaLogin(carrinho)
    usuario, perfil = tela_login.executar()

    if usuario:
        # Configura a interface principal com o usuário logado e perfil
        interface = InterfaceGraficaCarrinho(carrinho=carrinho)
        interface.usuario_atual = usuario
        interface.configurar_acesso_por_perfil(perfil)
        interface.executar()
    else:
        logging.info("Nenhum usuário autenticado. Encerrando o sistema.")