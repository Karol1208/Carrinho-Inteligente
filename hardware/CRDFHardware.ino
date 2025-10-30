#include <MFRC522.h>
#include <DIYables_Keypad.h>

// --- Configurações de Hardware ---
#define SS_PIN 53
#define RST_PIN 49
MFRC522 mfrc522(SS_PIN, RST_PIN);

const byte ROWS = 4;
const byte COLS = 4;
byte rowPins[ROWS] = {22, 23, 24, 25};
byte colPins[COLS] = {26, 27, 28, 29};
char keys[ROWS][COLS] = {
    {'1','2','3','A'}, {'4','5','6','B'},
    {'7','8','9','C'}, {'*','0','#','D'}
};
DIYables_Keypad keypad = DIYables_Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);
int buzzer = 11;
String inputPin = "";

// Pino da solenoide
#define SOLENOIDE_PIN 21 
const int TEMPO_ACIONAMENTO_SOLENOIDE = 5000; // 2 segundos

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  pinMode(buzzer, OUTPUT);

  // Configurar o pino da solenoide
  pinMode(SOLENOIDE_PIN, OUTPUT);
  // Garante que o relé comece DESLIGADO (solenoide desenergizada, haste retraída)
  digitalWrite(SOLENOIDE_PIN, HIGH); 
  
  Serial.println("ARDUINO_READY");
}

void loop() {
  // Lógica de leitura RFID (sem alterações)
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      uid += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
      uid += String(mfrc522.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    Serial.println("RFID:" + uid);
    tone(buzzer, 1000, 150);
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  }

  // Lógica de leitura do Teclado (sem alterações)
  char key = keypad.getKey();
  if (key) {
    tone(buzzer, 800, 50);
    if (key == '*' || key == '#') {
      inputPin = "";
    } else if (isDigit(key)) {
      inputPin += key;
    }
    if (inputPin.length() == 4) {
      Serial.println("PIN:" + inputPin);
      inputPin = "";
    }
  }

  // Aguarda comandos do Python
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void processCommand(String cmd) {
  cmd.trim(); 
  
  if (cmd.startsWith("ABRIR:")) {
    int drawerId = cmd.substring(6).toInt();
    
    Serial.print("ACK: Comando para gaveta ");
    Serial.print(drawerId);
    Serial.println(" recebido. Acionando trava.");
    tone(buzzer, 1200, 200);

    // Lógica de acionamento da solenoide
    Serial.println("Destravando o carrinho...");
    digitalWrite(SOLENOIDE_PIN, LOW);   // LIGA o relé -> Energiza a solenoide -> Haste avança
    delay(TEMPO_ACIONAMENTO_SOLENOIDE); // Mantém a haste avançada por 2 segundos
    digitalWrite(SOLENOIDE_PIN, HIGH);  // DESLIGA o relé -> Corta a energia -> Mola retrai a haste
    Serial.println("Carrinho travado.");
  }
  
  // --- NOVO CÓDIGO AQUI ---
  // Lógica para processar comandos de LED
  // Exemplo de comando: "LED:1:verde"
  if (cmd.startsWith("LED:")) {
    // Extrai o ID da gaveta e a cor
    int firstColon = cmd.indexOf(':');
    int secondColon = cmd.indexOf(':', firstColon + 1);
    
    if (secondColon > -1) {
      int drawerId = cmd.substring(firstColon + 1, secondColon).toInt();
      String color = cmd.substring(secondColon + 1);
      
      Serial.print("ACK: LED da Gaveta ");
      Serial.print(drawerId);
      Serial.print(" alterado para ");
      Serial.println(color);
      
      
    }
  }
}
