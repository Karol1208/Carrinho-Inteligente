import serial
import serial.tools.list_ports
import time
import threading
import logging


class HardwareArduino:
    @staticmethod
    def detectar_porta_arduino():
        """Detecta automaticamente a porta serial onde o Arduino está conectado."""
        portas = serial.tools.list_ports.comports()
        for porta in portas:
            if "Arduino" in porta.description or "CH340" in porta.description or "USB Serial" in porta.description:
                logging.info(f"Arduino detectado automaticamente na porta: {porta.device} ({porta.description})")
                return porta.device
        return None

    def __init__(self, port=None, baud_rate=9600):
        self.serial_port = None
        self.last_hardware_input = None
        self.is_running = False

        self.port = port if port else self.detectar_porta_arduino()
        self.baud_rate = baud_rate
        self.lock = threading.Lock()

        # Armazena o último estado conhecido de cada gaveta (1 a 7)
        self.estado_gavetas = {i: "FECHADA" for i in range(1, 8)}

        if self.port:
            try:
                self.serial_port = serial.Serial(self.port, self.baud_rate, timeout=1)
                logging.info(f"Conectado ao Arduino na porta {self.port} (Baud: {self.baud_rate}).")
                time.sleep(2)  # Aguarda o Arduino reiniciar e enviar "ARDUINO_READY"
                self.is_running = True
                self.thread = threading.Thread(target=self._read_from_port, daemon=True)
                self.thread.start()
            except serial.SerialException as e:
                logging.error(f"Erro ao conectar com o Arduino na porta {self.port}: {e}")
                self.is_running = False
        else:
            logging.warning("Nenhuma porta serial informada ou detectada para o Arduino.")
            self.is_running = False

    def _read_from_port(self):
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                logging.debug(f"SERIAL RECV: {line}")

                if line.startswith("RFID:") or line.startswith("PIN:"):
                    with self.lock:
                        self.last_hardware_input = line
                elif line.startswith("GAVETA_"):
                    # Exemplo esperado: GAVETA_3:ABERTA ou GAVETA_3:FECHADA
                    try:
                        partes = line.split(":")
                        if len(partes) >= 2:
                            nome_gaveta = partes[0]
                            estado = partes[1]
                            id_gaveta = int(nome_gaveta.split("_")[1])
                            with self.lock:
                                self.estado_gavetas[id_gaveta] = estado
                            logging.debug(f"Hardware Arduino: Gaveta {id_gaveta} -> {estado}")
                    except (IndexError, ValueError) as ve:
                        logging.warning(f"Erro ao parsear estado da gaveta '{line}': {ve}")
                elif line.startswith("OK:"):
                    if "ABRIR" in line:
                        logging.info(f"CONFIRMAÇÃO ARDUINO: {line}")
                    else:
                        logging.debug(f"CONFIRMAÇÃO ARDUINO (Rotina): {line}")

            except (serial.SerialException, TypeError, UnicodeDecodeError, OSError) as e:
                logging.warning(f"Falha na leitura serial do Arduino: {e}")
                self.is_running = False
                break
            except Exception as e:
                logging.error(f"Erro inesperado na thread de leitura serial: {e}")
                self.is_running = False
                break

    def ler_input_hardware(self):
        with self.lock:
            if self.last_hardware_input:
                data_to_return = self.last_hardware_input
                self.last_hardware_input = None
                partes = data_to_return.split(':', 1)
                if len(partes) == 2:
                    return partes[1]
        return None

    def abrir_gaveta_hardware(self, gaveta_id: int) -> bool:
        """Envia comando para o Arduino abrir uma gaveta."""
        if self.serial_port and self.is_running:
            try:
                self.serial_port.write(f"ABRIR:{gaveta_id}\n".encode('utf-8'))
                logging.debug(f"SERIAL SEND: ABRIR:{gaveta_id}")
                return True
            except (serial.SerialException, OSError) as e:
                logging.error(f"Falha ao enviar comando de abrir gaveta {gaveta_id}: {e}")
                self.is_running = False
                return False
        return False

    def fechar_gaveta_hardware(self, gaveta_id: int) -> bool:
        """Fechamento é mecânico (empurrar a gaveta). Sem comando ativo."""
        return True

    def definir_led_status(self, gaveta_id: int, status: str):
        """Envia comando para o Arduino alterar o status de um LED."""
        if self.serial_port and self.is_running:
            try:
                self.serial_port.write(f"LED:{gaveta_id}:{status}\n".encode('utf-8'))
            except (serial.SerialException, OSError) as e:
                logging.warning(f"Falha ao enviar status LED da gaveta {gaveta_id}: {e}")
                self.is_running = False

    def solicitar_status_gavetas(self):
        """Solicita ao Arduino que envie o estado de todas as gavetas (comando STATUS)."""
        if self.serial_port and self.is_running:
            try:
                self.serial_port.write(b"STATUS\n")
            except (serial.SerialException, OSError) as e:
                logging.warning(f"Falha ao enviar comando STATUS: {e}")
                self.is_running = False

    def gaveta_esta_aberta(self, gaveta_id: int) -> bool:
        """Verifica o status de um sensor de gaveta."""
        with self.lock:
            return self.estado_gavetas.get(gaveta_id) == "ABERTA"

    def close(self):
        """Fecha a porta serial de forma segura."""
        self.is_running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                logging.info("Conexão com Arduino finalizada.")
            except Exception as e:
                logging.warning(f"Erro ao fechar porta serial: {e}")
