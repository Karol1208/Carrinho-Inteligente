from dataclasses import dataclass
from typing import Optional

@dataclass
class UsuarioCartao:
    id: str
    nome: str
    cargo: str
    ativo: bool = True
    data_cadastro: str = None

@dataclass
class EventoGaveta:
    gaveta_id: int
    usuario_id: str
    acao: str  
    timestamp: str
    sucesso: bool

@dataclass
class Peca:
    id: int
    nome: str
    descricao: str
    gaveta_id: int
    quantidade_disponivel: int = 0
    ativo: bool = True

@dataclass
class RetiradaPeca:
    id: int
    usuario_id: str
    peca_id: int
    quantidade_retirada: int
    timestamp_retirada: str 

    quantidade_devolvida: int = 0
    timestamp_devolucao: Optional[str] = None
    status: str = "pendente" 