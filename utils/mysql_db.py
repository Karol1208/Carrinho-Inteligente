import mysql.connector
from mysql.connector import Error
import logging

class MySQLDatabase:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.conn = None
        self.cursor = None
        self.conectar()

    def conectar(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)
            logging.info("Conectado ao MySQL com sucesso.")
        except Error as e:
            logging.error(f"Erro ao conectar no MySQL: {e}")

    def adicionar_usuario(self, usuario):
        """
        Recebe um objeto UsuarioCartao e insere na tabela correspondente do MySQL.
        Ajuste o nome da tabela e colunas conforme seu schema MySQL.
        """
        try:
            sql = """
                INSERT INTO usuarios (id, nome, cargo, perfil, data_cadastro, ativo)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                nome=VALUES(nome),
                cargo=VALUES(cargo),
                perfil=VALUES(perfil),
                data_cadastro=VALUES(data_cadastro),
                ativo=VALUES(ativo)
            """
            valores = (
                usuario.id,
                usuario.nome,
                usuario.cargo,
                usuario.perfil,
                usuario.data_cadastro,
                int(usuario.ativo)  # supondo boolean armazenado como int
            )
            self.cursor.execute(sql, valores)
            self.conn.commit()
            logging.info(f"Usuário {usuario.nome} inserido/atualizado no MySQL.")
        except Error as e:
            logging.error(f"Erro ao adicionar usuário no MySQL: {e}")

    def fechar(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logging.info("Conexão MySQL fechada.")