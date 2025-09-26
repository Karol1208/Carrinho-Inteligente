import os
import datetime

from database import DatabaseManager
from core.cart import CarrinhoInteligenteAvancado
from models.entities import UsuarioCartao
from ui.interface import InterfaceGraficaCarrinho
from utils.config import setup_logging


def inicializar_sistema_exemplo(db_path: str = 'carrinho.db') -> CarrinhoInteligenteAvancado:
    """
    Inicializa o sistema com usuários de exemplo.
    """
    setup_logging()
    
    carrinho = CarrinhoInteligenteAvancado(db_path=db_path)
    usuarios_exemplo = [
        UsuarioCartao("12345", "João Silva", "Professor", data_cadastro=datetime.datetime.now().isoformat()),
        UsuarioCartao("67890", "Maria Santos", "Supervisora", data_cadastro=datetime.datetime.now().isoformat()),
        UsuarioCartao("11111", "Pedro Costa", "Líder", data_cadastro=datetime.datetime.now().isoformat()),
        UsuarioCartao("22222", "Ana Lima", "Aluno", data_cadastro=datetime.datetime.now().isoformat()),
    ]
    for usuario in usuarios_exemplo:
        carrinho.db.adicionar_usuario(usuario)
    import logging
    logging.info("Sistema inicializado com usuários de exemplo.")
    return carrinho

if __name__ == "__main__":
    carrinho = inicializar_sistema_exemplo()
    interface = InterfaceGraficaCarrinho(carrinho=carrinho)
    interface.executar()