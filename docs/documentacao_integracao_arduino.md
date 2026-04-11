# Documentação Técnica: Integração Sistema-Arduino (CRDF)

## Visão Geral
Este documento descreve as implementações, correções e otimizações realizadas na arquitetura de integração do sistema Python (CRDF) com o hardware (Arduino Mega). O objetivo principal das aterações foi garantir **estabilidade da interface gráfica (Tkinter)**, **remoção de conflitos de porta serial**, e **latência ultrabaixa** na resposta aos sensores infravermelhos.

---

## 1. Otimização do Firmware do Arduino (`arduino_programacao.ino`)
O código em linguaguem C++ embarcado no Arduino foi adaptado para "falar" um protocolo rigoroso que pudesse ser interpretado velozmente pelo Python.

- **Comando de Autodiagnóstico (`STATUS`)**:
  Antes, o comando imprimia relatórios formatados para leitura humana (ex: `Gaveta_1: FECHADA/OBST [OCIOSA]`).
  Foi substituído por um padrão `Chave:Valor` computacionalmente limpo: `GAVETA_X:ESTADO` (onde ESTADO = `FECHADA` ou `ABERTA`). Isso permite que o Python consiga invocar varreduras forçadas (Polling) quando necessário, além de receber eventos assíncronos.

---

## 2. Refatoração do Módulo de Hardware Python (`hardware/arduino.py`)
- O driver `HardwareArduino` foi estabelecido como a **Única Fonte de Verdade (Single Source of Truth)**.
- Adicionado um estado local em memória gerenciado via _Thread Locks_: `self.estado_gavetas = {i: "FECHADA" for i in range(1, 8)}`.
- O listener contínuo `_read_from_port` processa em tempo real a linha serial que começa com `GAVETA_` e sobreescreve imediatamente as variáveis isoladas do cache sem onerar o loop principal.
- Adicionado método `gaveta_esta_aberta(gaveta_id)` que consulta o cache limpo livre do serial no espaço do Python.

---

## 3. Correção de Confiltos de Hardware (`ui/abas/aba_principal.py`)
Havia uma sobreposição de portas COM (`COM4` x `COM2` x etc).
- As rotinas independentes `inicializar_serial()` e `ler_serial_arduino()` instanciadas unicamente na aba visual foram **excluídas**.
- Deste modo, a Aba Principal parou de competir pelo recurso da Porta Serial e passou a solicitar os dados passivamente da estância principal e unificada instigada na raiz pela variável `carrinho.hardware`.

---

## 4. Otimização do Loop Central e Latência (`core/cart.py`)
O sistema original sofria com latências de sincronização que oscilavam entre 10 até 14 segundos para perceber mudanças nos sensores físicos.

- **Latência Ultrabaixa (500ms):** A rotina assíncrona base `monitor_sistema` teve o seu `time.sleep(10)` decrescido para `time.sleep(0.5)`. Isso propicia atualizações visuais em menos de meio segundo, conferindo uma experiência de *"Tempo Real"*.
- **Desacoplamento Inteligente de Consulta Serial:** Para proteger o Arduino de saturação no buffer da serial (já que o loop roda a cada `0.5s`), um contador interno (`contador_status`) foi incorporado para invocar a escrita do `STATUS` integral apenas 1 vez ao decurso de 5 segundos. Assim obtem-se velocidade de resposta sem custo de gargalo no hardware.

---

## 5. Mitigação de Crashes e Exceções do Sistema

### 5.1 Tratamento de Sensoriamento Físico e Auto-Sincronismo
- Logs ríspidos foram substituídos por _Warnings_ organizados (`[ALERTA] SENSOR GAVETA 1: Física=ABERTA | Sistema=FECHADA. Sincronizando sistema...`).
- **Codificação de Caracteres**: A substituição do emoji de aviso `⚠` eliminou a falha grave `UnicodeEncodeError (CP1252)` que abalava permanentemente a Thread do Python sob sistemas Windows no momento da emissão dos logs no backend.
- **Auto-Sync Lógico:** Se caso o Arduino (Hardware) relatar uma gaveta fisicamente distante do que o Software entenda, a própria rotina _verificar_status_hardware()_ altera instantaneamente a variável orientada a eventos para refletir a realidade imposta pelo sensor (`abrir()` caso detecte luz, `fechar()` caso detecte obstáculo na Gaveta_X), eliminando desyncs contínuos infinitos.

### 5.2 Gerenciamento do Ciclo de Vida do Tkinter (`invalid command name ...`)
Ocorria quando callbacks temporizados (`.after()`) continuavam engatilhados quando a aba de login ou a interface unificada era encerrada abruptamente ou por tempo inativo, chamando instâncias destruídas na memória pela biblioteca C++ TCL subjacente.

- **Mecanismos de Prevenção WinFo:** Adicionada rotina de proteção `if not self.root.winfo_exists(): return` antes do processamento nos laços de `atualizar_status_periodico` (em `interface.py`).
- **Anulação Direta (Cancel):** Empregou-se o método explícito `root.after_cancel(id)` no evento interceptado nativamente `_on_close`. Desta forma, todas as ideles sub-rotinas são rigorosamente mortas no momento da fechada de janela não deixando rastros (mem leak) de chamadas "fantasmas", encerrando o terminal sem nenhum traço cinzento ou Stack Trace.
