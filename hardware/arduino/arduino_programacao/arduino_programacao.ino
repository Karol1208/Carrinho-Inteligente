#include <DIYables_Keypad.h>
#include <MFRC522.h>
#include <SPI.h>

// ========================
// --- CONFIGURAÇÕES RFID ---
// ========================
#define SS_PIN 53
#define RST_PIN 49
MFRC522 mfrc522(SS_PIN, RST_PIN);

// ========================
// --- CONFIGURAÇÃO TECLADO ---
// ========================
const byte ROWS = 4;
const byte COLS = 4;
byte rowPins[ROWS] = {22, 23, 24, 25};
byte colPins[COLS] = {26, 27, 28, 29};
char keys[ROWS][COLS] = {{'1', '2', '3', 'A'},
                         {'4', '5', '6', 'B'},
                         {'7', '8', '9', 'C'},
                         {'*', '0', '#', 'D'}};
DIYables_Keypad keypad =
    DIYables_Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

int buzzer = 11;
String inputPin = "";

// ========================
// --- GAVETAS E RELÉS ---
// ========================
#define NUM_GAVETAS 7
#define TRAVA_PIN 21
int gavetas[NUM_GAVETAS] = {20, 19, 18, 17, 16, 15, 14};

// ========================
// --- SENSORES IR ---
// ========================
int pinosSensores[NUM_GAVETAS] = {34, 35, 36, 37, 38, 39, 40};
int estadoSensores_anterior[NUM_GAVETAS];
bool sensorAtivo[NUM_GAVETAS] = {false};

const int TEMPO_ATRASO_GAVETA = 1000;
const int TEMPO_EMPURRE_GAVETA = 2000;

// ===========================================================
// --- SETUP ---
// ===========================================================
void setup() {
  Serial.begin(9600);
  delay(1000);
  SPI.begin();
  mfrc522.PCD_Init();

  pinMode(buzzer, OUTPUT);
  pinMode(TRAVA_PIN, OUTPUT);
  digitalWrite(TRAVA_PIN, HIGH);

  for (int i = 0; i < NUM_GAVETAS; i++) {
    pinMode(gavetas[i], OUTPUT);
    digitalWrite(gavetas[i], HIGH);
  }

  // --- LOG DE RECONHECIMENTO DOS SENSORES ---
  Serial.println("\n--- DIAGNOSTICO DE SENSORES ---");
  for (int i = 0; i < NUM_GAVETAS; i++) {
    pinMode(pinosSensores[i], INPUT_PULLUP);
    int leituraInicial = digitalRead(pinosSensores[i]);
    estadoSensores_anterior[i] = leituraInicial;

    Serial.print("Sensor ");
    Serial.print(i + 1);
    Serial.print(" (Pino ");
    Serial.print(pinosSensores[i]);
    Serial.print("): ");
    Serial.println(leituraInicial == LOW ? "OBSTACULO DETECTADO"
                                         : "LIMPO/LIVRE");
  }
  Serial.println("--------------------------------\n");
  Serial.println("ARDUINO_READY");
}

// ===========================================================
// --- LOOP PRINCIPAL ---
// ===========================================================
void loop() {
  lerRFID();
  lerTeclado();
  processarSerial();
  lerSensoresGavetas();
}

// ===========================================================
// --- LEITURA RFID ---
// ===========================================================
void lerRFID() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      uid += (mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
      uid += String(mfrc522.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    Serial.println("RFID:" + uid);
    tone(buzzer, 1000, 150);
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  }
}

// ===========================================================
// --- LEITURA TECLADO ---
// ===========================================================
void lerTeclado() {
  char key = keypad.getKey();
  if (key) {
    tone(buzzer, 800, 50);
    if (key == '*' || key == '#')
      inputPin = "";
    else if (isDigit(key))
      inputPin += key;
    if (inputPin.length() == 4) {
      Serial.println("PIN:" + inputPin);
      inputPin = "";
    }
  }
}

// ===========================================================
// --- PROCESSAMENTO SERIAL ---
// ===========================================================
void processarSerial() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equalsIgnoreCase("STATUS")) {
      // Envia estado de TODOS os sensores para o Python
      for (int i = 0; i < NUM_GAVETAS; i++) {
        Serial.print("GAVETA_");
        Serial.print(i + 1);
        Serial.print(":");
        Serial.println(digitalRead(pinosSensores[i]) == LOW ? "FECHADA"
                                                            : "ABERTA");
      }
    } else {
      processCommand(command);
    }
  }
}

// ===========================================================
// --- SENSORES IR: monitoramento de mudança de estado ---
// ===========================================================
void lerSensoresGavetas() {
  for (int i = 0; i < NUM_GAVETAS; i++) {
    // Só monitora gavetas que foram abertas via comando (sensorAtivo)
    if (!sensorAtivo[i])
      continue;

    int estadoAtual = digitalRead(pinosSensores[i]);

    if (estadoAtual != estadoSensores_anterior[i]) {
      if (estadoAtual == LOW) {
        // Gaveta sendo empurrada de volta (fechando)
        Serial.print("GAVETA_");
        Serial.print(i + 1);
        Serial.println(":FECHANDO");

        // Pulsa a trava para travar fisicamente ao fechar
        digitalWrite(TRAVA_PIN, LOW);
        delay(TEMPO_ATRASO_GAVETA);
        digitalWrite(TRAVA_PIN, HIGH);

        Serial.print("GAVETA_");
        Serial.print(i + 1);
        Serial.println(":FECHADA");

        tone(buzzer, 1500, 100);
        sensorAtivo[i] = false;
      } else {
        // Gaveta foi aberta fisicamente
        Serial.print("GAVETA_");
        Serial.print(i + 1);
        Serial.println(":ABERTA");
      }
      estadoSensores_anterior[i] = estadoAtual;
    }
  }
}

// ===========================================================
// --- ABERTURA DE GAVETA INDIVIDUAL ---
// ===========================================================
void abrirGaveta(int drawerId) {
  if (drawerId < 1 || drawerId > NUM_GAVETAS)
    return;
  int gavetaPin = gavetas[drawerId - 1];
  Serial.print("-> Abrindo Gaveta ");
  Serial.println(drawerId);
  digitalWrite(gavetaPin, LOW);
  delay(TEMPO_EMPURRE_GAVETA);
  digitalWrite(gavetaPin, HIGH);
  sensorAtivo[drawerId - 1] = true;
}

// ===========================================================
// --- PROCESSAMENTO DOS COMANDOS RECEBIDOS ---
// ===========================================================
void processCommand(String cmd) {
  if (cmd.startsWith("ABRIR:")) {
    String lista = cmd.substring(6);
    lista.trim();

    // Destrava a trava principal antes de qualquer abertura
    digitalWrite(TRAVA_PIN, LOW);
    delay(TEMPO_ATRASO_GAVETA);

    if (lista.equalsIgnoreCase("TODAS")) {
      // Abre todas as gavetas em sequência com trava ativa
      for (int i = 1; i <= NUM_GAVETAS; i++)
        abrirGaveta(i);
    } else {
      // Abre uma gaveta específica pelo ID
      int id = lista.toInt();
      if (id > 0 && id <= NUM_GAVETAS)
        abrirGaveta(id);
    }

    // Retrava APÓS abrir todas as gavetas solicitadas
    digitalWrite(TRAVA_PIN, HIGH);
    Serial.println("OK:ABRIR:" + lista);

  } else if (cmd.startsWith("LED:")) {
    // Controle de LED (confirmação apenas — implementar se houver LED RGB)
    Serial.println("OK:" + cmd);
  }
}