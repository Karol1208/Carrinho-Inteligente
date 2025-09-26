import sqlite3
import datetime
from typing import List, Optional

from models.entities import EventoGaveta, Peca, RetiradaPeca, UsuarioCartao


class DatabaseManager:
    def __init__(self, db_path='carrinho.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                cargo TEXT NOT NULL,
                ativo BOOLEAN NOT NULL DEFAULT 1,
                data_cadastro TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gaveta_id INTEGER NOT NULL,
                usuario_id TEXT NOT NULL,
                acao TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                sucesso BOOLEAN NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gavetas_config (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT,
                ativo BOOLEAN NOT NULL DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pecas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                gaveta_id INTEGER NOT NULL,
                quantidade_disponivel INTEGER NOT NULL DEFAULT 0,
                ativo BOOLEAN NOT NULL DEFAULT 1,
                FOREIGN KEY (gaveta_id) REFERENCES gavetas_config (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retiradas_pecas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id TEXT NOT NULL,
                peca_id INTEGER NOT NULL,
                quantidade_retirada INTEGER NOT NULL,
                quantidade_devolvida INTEGER NOT NULL DEFAULT 0,
                timestamp_retirada TEXT NOT NULL,
                timestamp_devolucao TEXT,
                status TEXT NOT NULL DEFAULT 'pendente',  -- 'pendente', 'devolvida', 'perdida'
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                FOREIGN KEY (peca_id) REFERENCES pecas (id)
            )
        ''')

        for i in range(1, 6):
            cursor.execute('''
                INSERT OR IGNORE INTO gavetas_config (id, nome, descricao, ativo)
                VALUES (?, ?, ?, ?)
            ''', (i, f'Gaveta {i}', f'Conteúdo da Gaveta {i}', 1))

        pecas_exemplo = [
            ("Parafuso M6", "Parafusos para fixação geral", 1, 100),
            ( "Chave de Fenda", "Ferramenta para parafusos", 2, 10),
            ( "Freio a Disco", "Peça de segurança veicular", 3, 20),
            ( "Óleo Lubrificante", "Lubrificação de motores", 4, 50),
            ( "Bateria 12V", "Alimentação elétrica", 5, 5),
        ]
        for nome, descricao, gaveta_id, qtd in pecas_exemplo:
            cursor.execute('''
                INSERT OR IGNORE INTO pecas (nome, descricao, gaveta_id, quantidade_disponivel)
                VALUES (?, ?, ?, ?)
            ''', (nome, descricao, gaveta_id, qtd))

        conn.commit()
        conn.close()

    def adicionar_usuario(self, usuario: UsuarioCartao):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO usuarios (id, nome, cargo, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario.id, usuario.nome, usuario.cargo, int(usuario.ativo),
              usuario.data_cadastro or datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def obter_usuario(self, usuario_id: str) -> Optional[UsuarioCartao]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, cargo, ativo, data_cadastro FROM usuarios WHERE id = ? AND ativo = 1', (usuario_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return UsuarioCartao(
                id=result[0], nome=result[1], cargo=result[2],
                ativo=bool(result[3]), data_cadastro=result[4]
            )
        return None

    def listar_usuarios(self) -> List[UsuarioCartao]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, cargo, ativo, data_cadastro FROM usuarios WHERE ativo = 1')
        results = cursor.fetchall()
        conn.close()
        return [UsuarioCartao(
            id=row[0], nome=row[1], cargo=row[2],
            ativo=bool(row[3]), data_cadastro=row[4]
        ) for row in results]

    def registrar_evento(self, evento: EventoGaveta):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO eventos (gaveta_id, usuario_id, acao, timestamp, sucesso)
            VALUES (?, ?, ?, ?, ?)
        ''', (evento.gaveta_id, evento.usuario_id, evento.acao, evento.timestamp, int(evento.sucesso)))
        conn.commit()
        conn.close()

    def obter_historico(self, limite=100) -> List[EventoGaveta]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT gaveta_id, usuario_id, acao, timestamp, sucesso
            FROM eventos ORDER BY timestamp DESC LIMIT ?
        ''', (limite,))
        results = cursor.fetchall()
        conn.close()
        return [EventoGaveta(
            gaveta_id=row[0], usuario_id=row[1], acao=row[2],
            timestamp=row[3], sucesso=bool(row[4])
        ) for row in results]

    def adicionar_peca(self, peca: Peca):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO pecas (id, nome, descricao, gaveta_id, quantidade_disponivel, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (peca.id, peca.nome, peca.descricao, peca.gaveta_id, peca.quantidade_disponivel, int(peca.ativo)))
        conn.commit()
        conn.close()

    def listar_pecas_por_gaveta(self, gaveta_id: int) -> List[Peca]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome, descricao, gaveta_id, quantidade_disponivel, ativo
            FROM pecas WHERE gaveta_id = ? AND ativo = 1
        ''', (gaveta_id,))
        results = cursor.fetchall()
        conn.close()
        return [Peca(
            id=row[0], nome=row[1], descricao=row[2], gaveta_id=row[3],
            quantidade_disponivel=row[4], ativo=bool(row[5])
        ) for row in results]

    def listar_todas_pecas(self) -> List[Peca]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, descricao, gaveta_id, quantidade_disponivel, ativo FROM pecas WHERE ativo = 1')
        results = cursor.fetchall()
        conn.close()
        return [Peca(
            id=row[0], nome=row[1], descricao=row[2], gaveta_id=row[3],
            quantidade_disponivel=row[4], ativo=bool(row[5])
        ) for row in results]

    def registrar_retirada_peca(self, usuario_id: str, peca_id: int, quantidade: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO retiradas_pecas (usuario_id, peca_id, quantidade_retirada, timestamp_retirada, status)
            VALUES (?, ?, ?, ?, 'pendente')
        ''', (usuario_id, peca_id, quantidade, timestamp))
        cursor.execute('''
            UPDATE pecas SET quantidade_disponivel = quantidade_disponivel - ? WHERE id = ?
        ''', (quantidade, peca_id))
        conn.commit()
        conn.close()

    def registrar_devolucao_peca(self, retirada_id: int, quantidade_devolvida: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute('''
            UPDATE retiradas_pecas 
            SET quantidade_devolvida = ?, timestamp_devolucao = ?, 
                status = CASE 
                    WHEN quantidade_retirada = quantidade_devolvida THEN 'devolvida' 
                    ELSE 'parcial' 
                END
            WHERE id = ?
        ''', (quantidade_devolvida, timestamp, retirada_id))
        cursor.execute('''
            SELECT peca_id, quantidade_retirada FROM retiradas_pecas WHERE id = ?
        ''', (retirada_id,))
        row = cursor.fetchone()
        if row:
            peca_id = row[0]
            qtd_original = row[1]
            qtd_pendente = qtd_original - quantidade_devolvida
            cursor.execute('''
                UPDATE pecas SET quantidade_disponivel = quantidade_disponivel + ? WHERE id = ?
            ''', (quantidade_devolvida, peca_id))
        conn.commit()
        conn.close()

    def obter_retiradas_pendentes_usuario(self, usuario_id: str) -> List[RetiradaPeca]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, usuario_id, peca_id, quantidade_retirada, quantidade_devolvida, 
                   timestamp_retirada, timestamp_devolucao, status
            FROM retiradas_pecas 
            WHERE usuario_id = ? AND status IN ('pendente', 'parcial')
            ORDER BY timestamp_retirada DESC
        ''', (usuario_id,))
        results = cursor.fetchall()
        conn.close()
        return [RetiradaPeca(
            id=row[0], usuario_id=row[1], peca_id=row[2], quantidade_retirada=row[3],
            quantidade_devolvida=row[4], timestamp_retirada=row[5],
            timestamp_devolucao=row[6], status=row[7]
        ) for row in results]

    def obter_peca_por_id(self, peca_id: int) -> Optional[Peca]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, descricao, gaveta_id, quantidade_disponivel, ativo FROM pecas WHERE id = ? AND ativo = 1', (peca_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return Peca(
                id=result[0], nome=result[1], descricao=result[2], gaveta_id=result[3],
                quantidade_disponivel=result[4], ativo=bool(result[5])
            )
        return None