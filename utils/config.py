import os
import datetime
import logging


def setup_logging():
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

class Config:
    """Centralized configuration for the application."""
    # Database
    DB_PATH = os.getenv('DB_PATH', 'carrinho.db')
    
    # Hardware
    MODO_HARDWARE = os.getenv('MODO_HARDWARE', 'simulador') # 'simulador' or 'real'
    PORTA_SERIAL = os.getenv('PORTA_SERIAL', 'COM9')
    
    # UI Constants
    INACTIVITY_TIMEOUT_MS = int(os.getenv('INACTIVITY_TIMEOUT_MS', 50000))
