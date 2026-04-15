import time
import logging


class SimuladorHardware:
    def __init__(self):
        self.sensores_gavetas = {i: False for i in range(1, 8)}  # False = fechada (7 gavetas)
        self.leds_status = {i: 'verde' for i in range(1, 8)}     # verde, vermelho, amarelo
        self.is_running = True  # O simulador está sempre "rodando"
        self.leitor_cartao_ativo = True

    def ler_input_hardware(self) -> str | None:
        """Alias para ler_rfid — mantém compatibilidade com a interface HardwareArduino."""
        return self.ler_rfid()

    def ler_rfid(self) -> str | None:
        """
        Simula a leitura do RFID.
        Retorna código RFID ou None se nada lido.
        PARA TESTES: Descomente a linha abaixo para retornar um código fixo.
        """
        # return "1234"  # ← DESCOMENTE PARA SIMULAR LEITURA AUTOMÁTICA
        return None

    def solicitar_status_gavetas(self):
        """Simula a solicitação de status (não faz nada no simulador)."""
        pass

    def abrir_gaveta_hardware(self, gaveta_id: int) -> bool:
        """Simula a abertura de uma gaveta individual."""
        try:
            if gaveta_id not in self.sensores_gavetas:
                raise ValueError(f"Gaveta {gaveta_id} inexistente no hardware")
            time.sleep(0.5)
            self.sensores_gavetas[gaveta_id] = True
            self.leds_status[gaveta_id] = 'verde'
            logging.info(f"[SIM] Gaveta {gaveta_id} ABERTA")
            return True
        except Exception as e:
            logging.error(f"Erro ao abrir gaveta {gaveta_id}: {e}")
            return False

    def fechar_gaveta_hardware(self, gaveta_id: int) -> bool:
        """Simula o fechamento de uma gaveta."""
        try:
            if gaveta_id not in self.sensores_gavetas:
                raise ValueError(f"Gaveta {gaveta_id} inexistente no hardware")
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

    def close(self):
        """Simula o encerramento do hardware."""
        logging.info("Hardware simulado finalizado.")
        self.is_running = False