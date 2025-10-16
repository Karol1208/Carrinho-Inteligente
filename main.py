import datetime
import logging
import sys
# Suas importações originais
from utils.mysql_db import MySQLDatabase
from core.cart import CarrinhoInteligenteAvancado
from ui.login import TelaLogin
from models.entities import UsuarioCartao
from ui.interface import InterfaceGraficaCarrinho
from utils.config import setup_logging


# --- Seção de Configuração do Hardware ---
MODO_HARDWARE = "real"  # Mude para "simulador" para testar sem o Arduino
PORTA_SERIAL = "COM4"   # Defina a porta COM correta do seu Arduino
# -----------------------------------------


def inicializar_sistema_exemplo(db_path: str = 'carrinho.db') -> tuple[CarrinhoInteligenteAvancado, MySQLDatabase]:
    setup_logging()
    
    # Inicializa o banco MySQL sempre
    mysql_db = MySQLDatabase(
        host='localhost',
        user='root',
        password='',
        database='carrinho'
    )

    if MODO_HARDWARE == "real":
        carrinho = CarrinhoInteligenteAvancado(db_path=db_path, modo_hardware='real', porta_serial=PORTA_SERIAL)
        if not carrinho.hardware or not carrinho.hardware.is_running:
            logging.error("Falha ao conectar com o hardware na porta %s.", PORTA_SERIAL)
            sys.exit("Encerrando: Hardware não detectado.")
    else:
        carrinho = CarrinhoInteligenteAvancado(db_path=db_path, modo_hardware='simulador')

    # Adiciona usuários de exemplo
    usuarios_exemplo = [
        UsuarioCartao(id="1234", nome="João Silva", cargo="Professor", perfil="admin", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="6789", nome="Maria Santos", cargo="Supervisora", perfil="admin", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="1111", nome="Pedro Costa", cargo="Líder", perfil="aluno", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="2222", nome="Ana Lima", cargo="Aluno", perfil="aluno", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
    ]

    for usuario in usuarios_exemplo:
        carrinho.db.adicionar_usuario(usuario)
        mysql_db.adicionar_usuario(usuario)
    
    logging.info("Sistema inicializado com usuários de exemplo.")
    return carrinho, mysql_db


if __name__ == "__main__":
    while True:
        carrinho, mysql_db = inicializar_sistema_exemplo()
        
        tela_login = TelaLogin(carrinho)
        usuario, perfil = tela_login.executar()

        if usuario:
            interface = InterfaceGraficaCarrinho(carrinho=carrinho, usuario_inicial=usuario)
            interface.executar()
        else:
            logging.info("Nenhum usuário autenticado. Encerrando o sistema.")
            if carrinho and hasattr(carrinho.hardware, 'close'):
                carrinho.hardware.close()
            mysql_db.fechar()
            break
