"""
Script de migration do banco de dados do Carrinho Inteligente.
Adiciona constraint UNIQUE na coluna `nome` da tabela `pecas`.
Deve ser executado uma vez para bancos existentes.
"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

def migrate(db_path='carrinho.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Verifica se já tem UNIQUE na coluna nome
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='pecas'")
    table_sql = c.fetchone()
    
    if table_sql and 'UNIQUE' in table_sql[0].upper():
        print("Migration já aplicada. Nada a fazer.")
        conn.close()
        return

    print("Aplicando migration: UNIQUE constraint em pecas.nome...")

    # 1. Remove duplicatas (mantém o de menor ID)
    c.execute('DELETE FROM pecas WHERE id NOT IN (SELECT MIN(id) FROM pecas GROUP BY nome)')
    n_removed = c.rowcount
    print(f"  Removidas {n_removed} duplicatas")

    # 2. Recria a tabela com UNIQUE
    c.execute('ALTER TABLE pecas RENAME TO pecas_old')
    c.execute('''
        CREATE TABLE pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            categoria TEXT,
            descricao TEXT,
            gaveta_id INTEGER NOT NULL,
            quantidade_disponivel INTEGER NOT NULL DEFAULT 0,
            tipo TEXT,
            ativo BOOLEAN NOT NULL DEFAULT 1,
            FOREIGN KEY (gaveta_id) REFERENCES gavetas_config (id)
        )
    ''')
    c.execute('''
        INSERT INTO pecas (id, nome, categoria, descricao, gaveta_id, quantidade_disponivel, tipo, ativo)
        SELECT id, nome, categoria, descricao, gaveta_id, quantidade_disponivel, tipo, ativo
        FROM pecas_old
    ''')
    c.execute('DROP TABLE pecas_old')

    # 3. Garante 7 gavetas
    for i in range(1, 8):
        c.execute(
            'INSERT OR IGNORE INTO gavetas_config (id, nome, descricao, ativo) VALUES (?, ?, ?, ?)',
            (i, f'Gaveta {i}', f'Conteúdo da Gaveta {i}', 1)
        )

    conn.commit()
    conn.close()
    
    c2 = sqlite3.connect(db_path).cursor()
    c2.execute("SELECT COUNT(*) FROM pecas WHERE ativo=1")
    total = c2.fetchone()[0]
    print(f"Migration aplicada com sucesso! Total de peças: {total}")

if __name__ == '__main__':
    migrate()
