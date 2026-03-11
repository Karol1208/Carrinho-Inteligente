import hashlib
import uuid

def hash_credencial(codigo: str) -> str:
    """Gera um hash SHA-256 para o código (PIN ou RFID)."""
    return hashlib.sha256(codigo.encode('utf-8')).hexdigest()

def gerar_uuid() -> str:
    """Gera um identificador único (UUID v4)."""
    return uuid.uuid4().hex
