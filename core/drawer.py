import datetime

class GavetaAvancada:
    def __init__(self, id: int, nome: str = None):
        self.id = id
        self.nome = nome or f"Gaveta {id}"
        self.aberta = False
        self.bloqueada = False
        self.ultima_abertura = None
        self.usuario_atual = None 
        self.tempo_limite_aberta = 300  # 5 minutos

    def pode_abrir(self) -> bool:
        return not self.bloqueada and not self.aberta

    def abrir(self, usuario_id: str) -> bool:
        if self.pode_abrir():
            self.aberta = True
            self.ultima_abertura = datetime.datetime.now()
            self.usuario_atual = usuario_id
            return True
        return False

    def fechar(self) -> bool:
        if self.aberta:
            self.aberta = False
            self.usuario_atual = None
            self.ultima_abertura = None
            return True
        return False

    def tempo_aberta(self) -> int:
        if self.aberta and self.ultima_abertura:
            return int((datetime.datetime.now() - self.ultima_abertura).total_seconds())
        return 0