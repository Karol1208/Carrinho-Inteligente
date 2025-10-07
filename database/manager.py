import logging
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
                perfil TEXT NOT NULL DEFAULT 'aluno',
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
                categoria TEXT,
                descricao TEXT,
                gaveta_id INTEGER NOT NULL,
                quantidade_disponivel INTEGER NOT NULL DEFAULT 0,
                tipo TEXT,
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
                status TEXT NOT NULL DEFAULT 'pendente',
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                FOREIGN KEY (peca_id) REFERENCES pecas (id)
            )
        ''')

        # Inserir gavetas padrão
        for i in range(1, 6):
            cursor.execute('''
                INSERT OR IGNORE INTO gavetas_config (id, nome, descricao, ativo)
                VALUES (?, ?, ?, ?)
            ''', (i, f'Gaveta {i}', f'Conteúdo da Gaveta {i}', 1))

        # Inserir peças exemplo
        pecas_exemplo = [
            ("Multímetro - ET1002", "Multímetro", "Medição Elétrica", 1, 12, "Diagnóstico"),
            ("Multímetro - ET1005", "Multímetro", "Medição Elétrica", 1, 1, "Diagnóstico"),
            ("Alicate Amperímetro e Multímetro - 10684", "Alicate", "Medição Elétrica", 2, 1, "Diagnóstico"),
            ("Termômetro - MT 350A", "Termômetro", "Medição Térmica", 2, 1, "Diagnóstico"),
            ("Osciloscópio", "Osciloscópio", "Medição Eletrônica", 3, 1, "Diagnóstico"),
            ("Chave T 6 mm", "Chaves", "6 mm", 4, 7, "ferramenta manual"),
            ("Chave T 850 mm", "Chaves", "850 mm", 4, 7, "ferramenta manual"),
            ("Chave T 860 mm", "Chaves", "860 mm", 4, 7, "ferramenta manual"),
            ("Chave T 870 mm", "Chaves", "870 mm", 4, 7, "ferramenta manual"),
            ("Chave T 880 mm", "Chaves", "880 mm", 4, 7, "ferramenta manual"),
            ("Chave T 890 mm", "Chaves", "890 mm", 4, 7, "ferramenta manual"),
            ("Chave T 900 mm", "Chaves", "900 mm", 4, 7, "ferramenta manual"),
            ("Chave T 910 mm", "Chaves", "910 mm", 4, 7, "ferramenta manual"),
            ("Chave T 920 mm", "Chaves", "920 mm", 4, 7, "ferramenta manual"),
            ("Chave T 930 mm", "Chaves", "930 mm", 4, 7, "ferramenta manual"),
            ("Chave T 940 mm", "Chaves", "940 mm", 4, 7, "ferramenta manual"),
            ("Chave T 950 mm", "Chaves", "950 mm", 4, 7, "ferramenta manual"),
            ("Chave T 960 mm", "Chaves", "960 mm", 4, 7, "ferramenta manual"),
            ("Chave T 970 mm", "Chaves", "970 mm", 4, 7, "ferramenta manual"),
            ("Chave T 980 mm", "Chaves", "980 mm", 4, 7, "ferramenta manual"),
            ("Chave T 990 mm", "Chaves", "990 mm", 4, 7, "ferramenta manual"),
            ("Chave T 1000 mm", "Chaves", "1000 mm", 4, 7, "ferramenta manual"),
        ]

        for nome, categoria, descricao, gaveta_id, qtd, tipo in pecas_exemplo:
            cursor.execute('''
                INSERT OR IGNORE INTO pecas (nome, categoria, descricao, gaveta_id, quantidade_disponivel, tipo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nome, categoria, descricao, gaveta_id, qtd, tipo))

        conn.commit()
        conn.close()

    def adicionar_usuario(self, usuario: UsuarioCartao):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO usuarios (id, nome, cargo, perfil, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (usuario.id, usuario.nome, usuario.cargo, usuario.perfil, int(usuario.ativo),
              usuario.data_cadastro or datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def obter_usuario_por_id(self, usuario_id: str) -> Optional[UsuarioCartao]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, cargo, perfil, ativo, data_cadastro FROM usuarios WHERE id = ? AND ativo = 1', (usuario_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return UsuarioCartao(
                id=result[0], nome=result[1], cargo=result[2],
                perfil=result[3], ativo=bool(result[4]), data_cadastro=result[5]
            )
        return None

    def listar_usuarios(self) -> List[UsuarioCartao]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, cargo, perfil, ativo, data_cadastro FROM usuarios WHERE ativo = 1')
        results = cursor.fetchall()
        conn.close()
        return [UsuarioCartao(
            id=row[0], nome=row[1], cargo=row[2], perfil=row[3],
            ativo=bool(row[4]), data_cadastro=row[5]
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
        if peca.id == 0:
            # Inserir nova peça
            cursor.execute('''
                INSERT INTO pecas (nome, categoria, descricao, gaveta_id, quantidade_disponivel, tipo, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (peca.nome, peca.categoria, peca.descricao, peca.gaveta_id, peca.quantidade_disponivel, peca.tipo, int(peca.ativo)))
        else:
            # Atualizar peça existente
            cursor.execute('''
                UPDATE pecas SET nome=?, categoria=?, descricao=?, gaveta_id=?, quantidade_disponivel=?, tipo=?, ativo=?
                WHERE id=?
            ''', (peca.nome, peca.categoria, peca.descricao, peca.gaveta_id, peca.quantidade_disponivel, peca.tipo, int(peca.ativo), peca.id))
        conn.commit()
        conn.close()

    def listar_pecas_por_gaveta(self, gaveta_id: int) -> List[Peca]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome, categoria, descricao, gaveta_id, quantidade_disponivel, tipo, ativo
            FROM pecas WHERE gaveta_id = ? AND ativo = 1
        ''', (gaveta_id,))
        results = cursor.fetchall()
        conn.close()
        return [Peca(
            id=row[0], nome=row[1], categoria=row[2], descricao=row[3], gaveta_id=row[4],
            quantidade_disponivel=row[5], tipo=row[6], ativo=bool(row[7])
        ) for row in results]

    def listar_todas_pecas(self) -> List[Peca]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, categoria, descricao, gaveta_id, quantidade_disponivel, tipo, ativo FROM pecas WHERE ativo = 1')
        results = cursor.fetchall()
        conn.close()
        return [Peca(
            id=row[0], nome=row[1], categoria=row[2], descricao=row[3], gaveta_id=row[4],
            quantidade_disponivel=row[5], tipo=row[6], ativo=bool(row[7])
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
            SELECT quantidade_retirada, quantidade_devolvida FROM retiradas_pecas WHERE id = ?
        ''', (retirada_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return
        qtd_retirada, qtd_devolvida_atual = row
        nova_qtd_devolvida = qtd_devolvida_atual + quantidade_devolvida
        status = 'devolvida' if nova_qtd_devolvida >= qtd_retirada else 'parcial'
        cursor.execute('''
            UPDATE retiradas_pecas
            SET quantidade_devolvida = ?, timestamp_devolucao = ?, status = ?
            WHERE id = ?
        ''', (nova_qtd_devolvida, timestamp, status, retirada_id))
        cursor.execute('''
            UPDATE pecas SET quantidade_disponivel = quantidade_disponivel + ? WHERE id = (
                SELECT peca_id FROM retiradas_pecas WHERE id = ?
            )
        ''', (quantidade_devolvida, retirada_id))
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
        cursor.execute('SELECT id, nome, categoria, descricao, gaveta_id, quantidade_disponivel, tipo, ativo FROM pecas WHERE id = ? AND ativo = 1', (peca_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return Peca(
                id=result[0], nome=result[1], categoria=result[2], descricao=result[3], gaveta_id=result[4],
                quantidade_disponivel=result[5], tipo=result[6], ativo=bool(result[7])
            )
        return None

    def obter_retiradas_pendentes_por_peca(self, peca_id: int) -> List[RetiradaPeca]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, usuario_id, peca_id, quantidade_retirada, quantidade_devolvida,
                   timestamp_retirada, timestamp_devolucao, status
            FROM retiradas_pecas
            WHERE peca_id = ? AND status IN ('pendente', 'parcial')
        ''', (peca_id,))
        rows = cursor.fetchall()
        conn.close()
        return [RetiradaPeca(
            id=row[0], usuario_id=row[1], peca_id=row[2], quantidade_retirada=row[3],
            quantidade_devolvida=row[4], timestamp_retirada=row[5],
            timestamp_devolucao=row[6], status=row[7]
        ) for row in rows]
    

    def limpar_historico(self):
        """Apaga todos os registros da tabela de histórico."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM eventos')
            conn.commit()
            conn.close()
            logging.info("Tabela de eventos (histórico) limpa com sucesso.")
            return True
        except sqlite3.Error as e:
            logging.error(f"Erro ao limpar a tabela de eventos: {e}")
            return False

    def remover_peca(self, peca_id: int):
        """Desativa uma peça no banco de dados (soft delete)."""
        conn = sqlite3.connect(self.db_path) # Correção: Usando a conexão direta
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE pecas SET ativo = 0 WHERE id = ?', (peca_id,))
            conn.commit()
            logging.info(f"Peça com ID {peca_id} foi desativada.")
            return True
        except sqlite3.Error as e:
            logging.error(f"Erro ao desativar a peça com ID {peca_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def obter_todas_retiradas_pendentes(self) -> List[RetiradaPeca]:
        """Retorna uma lista de todas as retiradas com status 'pendente' ou 'parcial'."""
        conn = sqlite3.connect(self.db_path) # Correção: Usando a conexão direta
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, usuario_id, peca_id, quantidade_retirada, quantidade_devolvida,
                    timestamp_retirada, timestamp_devolucao, status
                FROM retiradas_pecas
                WHERE status IN ('pendente', 'parcial')
                ORDER BY timestamp_retirada ASC
            ''')
            results = cursor.fetchall()
            return [RetiradaPeca(
                id=row[0], usuario_id=row[1], peca_id=row[2], quantidade_retirada=row[3],
                quantidade_devolvida=row[4], timestamp_retirada=row[5],
                timestamp_devolucao=row[6], status=row[7]
            ) for row in results]
        finally:
            conn.close()

