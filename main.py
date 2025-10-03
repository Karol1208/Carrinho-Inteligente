import datetime
import logging

from core.cart import CarrinhoInteligenteAvancado
from models.entities import UsuarioCartao
from ui.interface import InterfaceGraficaCarrinho
from utils.config import setup_logging  


from ui.login import TelaLogin

def inicializar_sistema_exemplo(db_path: str = 'carrinho.db') -> CarrinhoInteligenteAvancado:
    setup_logging() 
    carrinho = CarrinhoInteligenteAvancado(db_path=db_path)

    usuarios_exemplo = [
        UsuarioCartao(id="12345", nome="João Silva", cargo="Professor", perfil="admin", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="67890", nome="Maria Santos", cargo="Supervisora", perfil="admin", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="11111", nome="Pedro Costa", cargo="Líder", perfil="aluno", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
        UsuarioCartao(id="22222", nome="Ana Lima", cargo="Aluno", perfil="aluno", data_cadastro=datetime.datetime.now().isoformat(), ativo=True),
    ]
    for usuario in usuarios_exemplo:
        carrinho.db.adicionar_usuario(usuario)

    logging.info("Sistema inicializado com usuários de exemplo.")
    return carrinho

if __name__ == "__main__":
    carrinho = inicializar_sistema_exemplo()

    tela_login = TelaLogin(carrinho)
    usuario, perfil = tela_login.executar()

    if usuario:
        interface = InterfaceGraficaCarrinho(carrinho=carrinho, usuario_inicial=usuario)
        interface.configurar_acesso_por_perfil(perfil)
        interface.executar()
    else:
        logging.info("Nenhum usuário autenticado. Encerrando o sistema.")