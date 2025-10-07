import serial
import time
import threading

class HardwareArduino:
    def __init__(self, port, baud_rate=9600):
        self.serial_port = None
        self.last_hardware_input = None
        self.is_running = False
        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
            print(f"Conectado ao Arduino na porta {port}.")
            time.sleep(2) # Espera o Arduino reiniciar e enviar "ARDUINO_READY"
            self.is_running = True
            self.thread = threading.Thread(target=self._read_from_port, daemon=True)
            self.thread.start()
        except serial.SerialException as e:
            print(f"Erro ao conectar com o Arduino: {e}")
            self.is_running = False

    def _read_from_port(self):
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line.startswith("RFID:") or line.startswith("PIN:"):
                    self.last_hardware_input = line
            except (serial.SerialException, TypeError):
                # A porta pode ter sido fechada, encerra o loop
                self.is_running = False
                break

    def ler_input_hardware(self):
        if self.last_hardware_input:
            data_to_return = self.last_hardware_input
            self.last_hardware_input = None
            return data_to_return.split(':')[1]
        return None
    
    # --- MÉTODOS ADICIONADOS PARA COMPATIBILIDADE ---
    
    def abrir_gaveta_hardware(self, gaveta_id):
        """Envia comando para o Arduino abrir uma gaveta."""
        if self.serial_port and self.is_running:
            self.serial_port.write(f"ABRIR:{gaveta_id}\n".encode('utf-8'))
            return True
        return False

    def fechar_gaveta_hardware(self, gaveta_id):
        """Simula o fechamento. Em hardware real, isso geralmente é mecânico."""
        # O Arduino não precisa de um comando para isso, mas o método deve existir.
        return True

    def definir_led_status(self, gaveta_id, status):
        """Envia comando para o Arduino alterar o status de um LED."""
        # Status pode ser 'verde', 'amarelo', 'vermelho'
        if self.serial_port and self.is_running:
            self.serial_port.write(f"LED:{gaveta_id}:{status}\n".encode('utf-8'))

    def gaveta_esta_aberta(self, gaveta_id):
        """Verifica o status de um sensor de gaveta."""
        # Esta é uma função placeholder. Para funcionar de verdade, o Arduino
        # precisaria de sensores de porta e de um comando para consultar seu estado.
        # Por enquanto, retornamos False para evitar inconsistências.
        return False

    def close(self):
        """Fecha a porta serial de forma segura."""
        self.is_running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Conexão com Arduino finalizada.")