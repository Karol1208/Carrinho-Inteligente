# CRDF - Carrinho Inteligente de Ferramentas (SENAI)

![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Status](https://img.shields.io/badge/status-funcional-success)

## 📖 Descrição do Projeto

O **CRDF (Controle de Retirada e Devolução de Ferramentas)** é um sistema de carrinho de ferramentas inteligente desenvolvido para otimizar o gerenciamento e a rastreabilidade de equipamentos em ambientes educacionais, como o SENAI. A solução utiliza um microcontrolador Arduino integrado a um software com interface gráfica em Python para controlar o acesso às gavetas e registrar todas as operações em um banco de dados local.

O sistema permite a autenticação de usuários (professores e alunos) através de tags **RFID** ou **PIN**, garantindo que apenas pessoas autorizadas tenham acesso às ferramentas e que cada retirada ou devolução seja devidamente registrada.

---

## 🗃️ Banco de Dados MySQL

1. **Instale o MySQL** (se ainda não tiver):
   - [Download MySQL](https://dev.mysql.com/downloads/)

2. **Configure o arquivo `database/init_db.py`** com seu usuário e senha MySQL.

3. **Rode o script de inicialização**:
   ```bash
   python database/init_db.py
   
---

## ✨ Funcionalidades Principais

* **Autenticação Dupla:** Login via tags RFID ou teclado matricial (PIN de 4 dígitos).
* **Controle de Acesso por Perfil:**
    * **Admin (Professor):** Acesso a todas as funcionalidades, incluindo gerenciamento de usuários, inventário e histórico.
    * **Aluno:** Acesso restrito ao painel de retirada e devolução de ferramentas.
* **Gerenciamento de Gavetas:** Controle de abertura individual das gavetas por meio de relés acionados pelo Arduino.
* **Interface Gráfica Completa:** Interface intuitiva desenvolvida em Tkinter com abas para:
    * Painel de Retirada
    * Inventário de Peças
    * Gerenciamento de Usuários
    * Histórico de Eventos
* **Segurança:**
    * **Timer de Inatividade:** Desloga o usuário automaticamente após um período sem atividade.
    * **Botão de Logout:** Permite encerrar a sessão manualmente.
* **Funcionalidades de Administrador:**
    * Cadastrar novas tags RFID para novos usuários diretamente pela interface.
    * Adicionar, atualizar e remover peças do inventário.
    * Apagar todo o histórico de eventos.
    * Abrir todas as gavetas simultaneamente para modo de manutenção.
* **Monitoramento em Tempo Real:** Feedback visual do status das gavetas (aberta/fechada) e alertas para gavetas abertas por muito tempo.

---

## 💻 Tecnologias Utilizadas

* **Back-end & Interface:**
    * ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
    * **Tkinter:** Para a construção da interface gráfica.
    * **Pillow (PIL):** Para manipulação de imagens na interface.
    * **pyserial:** Para comunicação serial com o Arduino.
    * **SQLite3:** Para o banco de dados local.

* **Hardware:**
    * ![Arduino](https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white)
    * **Leitor RFID-RC522:** Para autenticação com tags.
    * **Teclado Matricial 4x4:** Para autenticação com PIN.
    * **Módulo de Relés:** Para acionamento das travas das gavetas.
    * **LEDs e Buzzer:** Para feedback visual e sonoro.

---

## 🚀 Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto.

### Pré-requisitos

* **Python 3.8** ou superior.
* **IDE do Arduino** instalada.
* Bibliotecas Arduino: `MFRC522.h` e `DIYables_Keypad.h` (ou similar).

### 1. Clonar o Repositório

```bash
git clone [Ainda não público]
cd Carrinho-Inteligente
