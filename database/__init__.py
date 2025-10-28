from .manager import DatabaseManager
from .conexao import ConexaoDB
import os
import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self, host="localhost", user="root", password="", database="carrinho"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Conecta ao banco de dados MySQL"""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            print(f"[INFO] Conectado ao banco '{self.database}'")
        except Error as e:
            print(f"[ERRO] Falha na conexão: {e}")

    def execute_query(self, query):
        """Executa uma query SQL"""
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Error as e:
            print(f"[ERRO] Falha ao executar query: {e}")

    def execute_script_from_file(self, filepath):
        """Executa um arquivo SQL inteiro"""
        if not os.path.exists(filepath):
            print(f"[ERRO] Arquivo SQL não encontrado: {filepath}")
            return

        with open(filepath, "r", encoding="utf-8") as f:
            sql_script = f.read()

        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if stmt:
                self.execute_query(stmt)

# Caminho absoluto do schema.sql dentro da pasta database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

# Inicializa o gerenciador de banco e aplica o schema automaticamente
db_manager = DatabaseManager()
db_manager.execute_script_from_file(SCHEMA_PATH)

