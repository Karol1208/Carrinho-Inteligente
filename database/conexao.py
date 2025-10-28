import mysql.connector
from mysql.connector import Error

class ConexaoDB:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Conexão MySQL estabelecida com sucesso!")
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            self.connection = None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão MySQL encerrada.")
    
    def execute_query(self, query, params=None):
        if not self.connection or not self.connection.is_connected():
            print("Não há conexão ativa com o banco de dados.")
            return
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            print("Query executada com sucesso.")
        except Error as e:
            print(f"Erro ao executar query: {e}")
        finally:
            cursor.close()
    
    def fetch_query(self, query, params=None):
        if not self.connection or not self.connection.is_connected():
            print("Não há conexão ativa com o banco de dados.")
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Erro ao buscar dados: {e}")
            return None
        finally:
            cursor.close()
