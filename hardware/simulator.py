import time
import logging


class SimuladorHardware:
    def __init__(self):
        self.sensores_gavetas = {i: False for i in range(1, 6)}  # False = fechada
        self.leds_status = {i: 'verde' for i in range(1, 6)}  # verde, vermelho, amarelo
        self.leitor_cartao_ativo = True


    def ler_rfid(self) -> str | None:
        """
        Simula a leitura do RFID.
        Retorna código RFID ou None se nada lido.
        """
        # Aqui você pode implementar simulação ou integração real
        return None


    def abrir_gaveta_hardware(self, gaveta_id: int) -> bool:
        try:
            if gaveta_id not in self.sensores_gavetas:
                raise ValueError("Gaveta inexistente no hardware")
            time.sleep(0.5)
            self.sensores_gavetas[gaveta_id] = True
            self.leds_status[gaveta_id] = 'verde'
            return True
        except Exception as e:
            logging.error(f"Erro ao abrir gaveta {gaveta_id}: {e}")
            return False


    def fechar_gaveta_hardware(self, gaveta_id: int) -> bool:
        try:
            if gaveta_id not in self.sensores_gavetas:
                raise ValueError("Gaveta inexistente no hardware")
            time.sleep(0.3)
            self.sensores_gavetas[gaveta_id] = False
            self.leds_status[gaveta_id] = 'verde'
            return True
        except Exception as e:
            logging.error(f"Erro ao fechar gaveta {gaveta_id}: {e}")
            return False


    def gaveta_esta_aberta(self, gaveta_id: int) -> bool:
        return self.sensores_gavetas.get(gaveta_id, False)


    def definir_led_status(self, gaveta_id: int, cor: str):
        if gaveta_id in self.leds_status:
            self.leds_status[gaveta_id] = cor

