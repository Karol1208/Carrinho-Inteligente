import os
import datetime
import logging

def setup_logging():
    """
    Configura o logging para o projeto.
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')

    LOG_FILENAME = f'logs/carrinho_{datetime.date.today().isoformat()}.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILENAME),
            logging.StreamHandler()
        ]
    )