import sqlite3
import logging
import datetime
from typing import List, Optional, Dict
import time
import threading
from dataclasses import dataclass
from database.manager import DatabaseManager
from models.entities import UsuarioCartao, EventoGaveta, Peca, RetiradaPeca
from core.drawer import GavetaAvancada
from hardware.arduino import HardwareArduino
from hardware.simulator import SimuladorHardware


class CarrinhoInteligenteAvancado:
    def __init__(self, db_path: str = 'carrinho.db', modo_hardware: str = 'real', porta_serial: Optional[str] = None):
        """
        Inicializa o carrinho com seleção de hardware.
        modo_hardware: 'real' tenta conectar ao Arduino; 'simulador' usa o simulador.
        porta_serial: porta explícita (ex: 'COM3'). Se None, detecta automaticamente.
        """
        self.db = DatabaseManager(db_path=db_path)

        # Escolha do hardware
        if modo_hardware == 'real':
            self.hardware = HardwareArduino(port=porta_serial)
            if not self.hardware.is_running:
                logging.warning("Hardware real não conectado. Recaindo para o modo simulador.")
                self.hardware = SimuladorHardware()
        else:
            logging.info("Iniciando em MODO SIMULADOR.")
            self.hardware = SimuladorHardware()

        self.gavetas = {i: GavetaAvancada(i, f"Gaveta {i}") for i in range(1, 8)}
        self.sistema_ativo = True
        self.modo_manutencao = False
        self.alertas_ativos = []

        # Sistema de callbacks RFID — usado pelo login.py e cadastro.py
        self._rfid_callbacks = []

        # Controle de flood para tokens inválidos
        self._ultimo_token_invalido = None
        self._ultimo_token_invalido_ts = 0.0
        self._cooldown_token_invalido_s = 1.5

        self.monitor_thread = threading.Thread(target=self.monitor_sistema, daemon=True)
        self.monitor_thread.start()

    # ---------------------------------------------------------------
    # CALLBACKS RFID
    # ---------------------------------------------------------------

    def registrar_callback_rfid(self, callback):
        """Registra uma função a ser chamada quando um cartão RFID for detectado."""
        if callback not in self._rfid_callbacks:
            self._rfid_callbacks.append(callback)

    def remover_callback_rfid(self, callback):
        """Remove um callback RFID registrado."""
        if callback in self._rfid_callbacks:
            self._rfid_callbacks.remove(callback)

    def _notificar_rfid_lido(self, codigo: str):
        """Distribui o código RFID para todos os ouvintes registrados."""
        for callback in list(self._rfid_callbacks):
            try:
                callback(codigo)
            except Exception as e:
                logging.error(f"Erro ao executar callback RFID: {e}")

    # ---------------------------------------------------------------
    # VALIDAÇÃO E CONTROLE DE ACESSO
    # ---------------------------------------------------------------

    def validar_cartao(self, codigo_cartao: str) -> Optional[UsuarioCartao]:
        if not codigo_cartao:
            return None

        codigo_cartao = str(codigo_cartao).strip()
        if not codigo_cartao:
            return None

        usuario = self.db.obter_usuario_por_id(codigo_cartao)
        if usuario:
            logging.info(f"Cartão validado: {usuario.nome} ({usuario.id})")
            self._ultimo_token_invalido = None
            self._ultimo_token_invalido_ts = 0.0
            return usuario

        agora = time.time()
        if (
            self._ultimo_token_invalido == codigo_cartao
            and (agora - self._ultimo_token_invalido_ts) < self._cooldown_token_invalido_s
        ):
            logging.debug(
                f"Token inválido repetido em cooldown ({self._cooldown_token_invalido_s}s): {codigo_cartao}"
            )
            return None

        self._ultimo_token_invalido = codigo_cartao
        self._ultimo_token_invalido_ts = agora
        logging.warning(f"Cartão inválido/não autorizado: {codigo_cartao}")
        return None

    # ---------------------------------------------------------------
    # CONTROLE DAS GAVETAS
    # ---------------------------------------------------------------

    def abrir_gaveta(self, gaveta_id: int, codigo_cartao: str) -> bool:
        usuario = self.validar_cartao(codigo_cartao)
        sucesso = False
        if not usuario:
            self.registrar_tentativa_acesso(gaveta_id, codigo_cartao, "abrir", False, "Cartão não autorizado")
            return False
        if gaveta_id not in self.gavetas:
            logging.warning(f"Tentativa de acesso a gaveta inexistente: {gaveta_id}")
            return False
        gaveta = self.gavetas[gaveta_id]
        if gaveta.pode_abrir():
            if self.hardware.abrir_gaveta_hardware(gaveta_id):
                sucesso = gaveta.abrir(usuario.id)
                if sucesso:
                    self.hardware.definir_led_status(gaveta_id, 'verde')
                    logging.info(f"Gaveta {gaveta_id} aberta por {usuario.nome} ({usuario.id})")
                    logging.info(f"Possível retirada de peças da Gaveta {gaveta_id} por {usuario.nome}")
        else:
            logging.info(f"Gaveta {gaveta_id} já está aberta ou bloqueada.")
        evento = EventoGaveta(
            gaveta_id=gaveta_id,
            usuario_id=usuario.id,
            acao="abrir",
            timestamp=datetime.datetime.now().isoformat(),
            sucesso=sucesso
        )
        self.db.registrar_evento(evento)
        return sucesso

    def fechar_gaveta(self, gaveta_id: int, codigo_cartao: str = None) -> bool:
        gaveta = self.gavetas.get(gaveta_id)
        if not gaveta:
            return False
        sucesso = False
        usuario_id = codigo_cartao or gaveta.usuario_atual or "sistema"
        if gaveta.aberta:
            if self.hardware.fechar_gaveta_hardware(gaveta_id):
                sucesso = gaveta.fechar()
                if sucesso:
                    self.hardware.definir_led_status(gaveta_id, 'verde')
                    logging.info(f"Gaveta {gaveta_id} fechada")
                    logging.info(f"Possível devolução de peças da Gaveta {gaveta_id}")
        evento = EventoGaveta(
            gaveta_id=gaveta_id,
            usuario_id=usuario_id,
            acao="fechar",
            timestamp=datetime.datetime.now().isoformat(),
            sucesso=sucesso
        )
        self.db.registrar_evento(evento)
        return sucesso

    def abrir_todas_gavetas_manutencao(self, usuario_id: str) -> bool:
        """Abre todas as gavetas para manutenção. Requer perfil de admin."""
        usuario = self.db.obter_usuario_por_id(usuario_id)
        if not usuario or usuario.perfil != 'admin':
            logging.warning(f"Tentativa não autorizada de abrir todas as gavetas pelo usuário ID: {usuario_id}")
            return False

        logging.info(f"MODO MANUTENÇÃO: Admin {usuario.nome} abrindo todas as gavetas.")
        sucesso_total = True
        for gaveta_id, gaveta in self.gavetas.items():
            if not gaveta.aberta:
                if self.hardware.abrir_gaveta_hardware(gaveta_id):
                    gaveta.abrir(usuario.id)
                    self.db.registrar_evento(EventoGaveta(
                        gaveta_id=gaveta_id,
                        usuario_id=usuario.id,
                        acao='abrir_admin',
                        timestamp=datetime.datetime.now().isoformat(),
                        sucesso=True
                    ))
                    logging.info(f"  Gaveta {gaveta_id}: ABERTA")
                else:
                    sucesso_total = False
                    logging.error(f"  Gaveta {gaveta_id}: FALHA ao abrir")
        return sucesso_total

    def registrar_tentativa_acesso(self, gaveta_id: int, codigo_cartao: str, acao: str, sucesso: bool, motivo: str = ""):
        logging.warning(f"Tentativa de acesso negada - Gaveta: {gaveta_id}, Cartão: {codigo_cartao}, Motivo: {motivo}")
        evento = EventoGaveta(
            gaveta_id=gaveta_id,
            usuario_id=codigo_cartao,
            acao=acao,
            timestamp=datetime.datetime.now().isoformat(),
            sucesso=sucesso
        )
        self.db.registrar_evento(evento)

    # ---------------------------------------------------------------
    # MONITOR DO SISTEMA (thread daemon)
    # ---------------------------------------------------------------

    def monitor_sistema(self):
        """
        Loop principal de monitoramento:
        - Gerencia os LEDs de status das gavetas.
        - Solicita STATUS ao Arduino a cada ~5 segundos.
        - Reconcilia estado lógico vs. sensor físico.
        - Faz polling do RFID e dispara callbacks.
        """
        contador_status = 0
        while self.sistema_ativo:
            try:
                # --- Gestão dos LEDs ---
                for gaveta_id, gaveta in self.gavetas.items():
                    if gaveta.aberta:
                        tempo_aberta = gaveta.tempo_aberta()
                        if tempo_aberta > 600:  # 10 minutos
                            usuario = self.db.obter_usuario_por_id(gaveta.usuario_atual) if gaveta.usuario_atual else None
                            nome_usuario = usuario.nome if usuario else (gaveta.usuario_atual or "Desconhecido")
                            alerta_msg = f"Gaveta {gaveta_id} aberta há mais de 10 minutos por {nome_usuario}. Favor fechar!"
                            if alerta_msg not in [a['mensagem'] for a in self.alertas_ativos]:
                                self.adicionar_alerta(alerta_msg)
                                logging.warning(alerta_msg)
                            self.hardware.definir_led_status(gaveta_id, 'vermelho')
                        elif tempo_aberta > 300:  # 5 minutos
                            self.hardware.definir_led_status(gaveta_id, 'amarelo')
                        else:
                            self.hardware.definir_led_status(gaveta_id, 'verde')
                    else:
                        self.hardware.definir_led_status(gaveta_id, 'verde')

                # --- Sincronia com hardware ---
                self.verificar_status_hardware(contador_status)

                # --- Polling RFID → callbacks ---
                try:
                    codigo_lido = self.hardware.ler_input_hardware()
                    if codigo_lido:
                        self._notificar_rfid_lido(codigo_lido)
                except Exception as e:
                    logging.debug(f"Erro ao ler hardware: {e}")

                contador_status += 1
                if contador_status >= 10:
                    contador_status = 0

                time.sleep(0.5)  # Ciclo de 500ms — comprovado como estável

            except Exception as e:
                logging.error(f"Erro no monitor do sistema: {e}")

    def verificar_status_hardware(self, contador: int = 0):
        """
        Solicita STATUS ao Arduino a cada ~5 s (quando contador == 0)
        e reconcilia o estado lógico com o sensor físico.
        """
        if contador == 0 and hasattr(self.hardware, 'solicitar_status_gavetas'):
            self.hardware.solicitar_status_gavetas()

        for gaveta_id in self.gavetas:
            hardware_aberta = self.hardware.gaveta_esta_aberta(gaveta_id)
            software_aberta = self.gavetas[gaveta_id].aberta

            if hardware_aberta != software_aberta:
                estado_fisico = "ABERTA" if hardware_aberta else "FECHADA"
                estado_logico = "ABERTA" if software_aberta else "FECHADA"
                msg_alerta = (
                    f"[ALERTA] SENSOR GAVETA {gaveta_id}: "
                    f"Física={estado_fisico} | Sistema={estado_logico}. "
                    f"Sincronizando sistema com o hardware..."
                )
                self.adicionar_alerta(msg_alerta)
                logging.warning(msg_alerta)
                print(msg_alerta)  # visibilidade rápida no terminal

                # Auto-sincroniza
                if hardware_aberta:
                    self.gavetas[gaveta_id].aberta = True
                else:
                    self.gavetas[gaveta_id].fechar()

    # ---------------------------------------------------------------
    # ALERTAS
    # ---------------------------------------------------------------

    def adicionar_alerta(self, mensagem: str):
        alerta = {'mensagem': mensagem, 'timestamp': datetime.datetime.now().isoformat()}
        self.alertas_ativos.append(alerta)
        if len(self.alertas_ativos) > 20:
            self.alertas_ativos.pop(0)

    # ---------------------------------------------------------------
    # PEÇAS E RETIRADAS
    # ---------------------------------------------------------------

    def listar_pecas_por_gaveta(self, gaveta_id: int) -> List[Peca]:
        return self.db.listar_pecas_por_gaveta(gaveta_id)

    def listar_todas_pecas(self) -> List[Peca]:
        return self.db.listar_todas_pecas()

    def adicionar_peca(self, peca: Peca) -> bool:
        if peca.quantidade_disponivel < 0:
            logging.warning("Quantidade inválida para peça.")
            return False
        self.db.adicionar_peca(peca)
        logging.info(f"Peça adicionada/atualizada: {peca.nome} na Gaveta {peca.gaveta_id}")
        return True

    def registrar_retirada_peca(self, usuario_id: str, peca_id: int, quantidade: int) -> bool:
        if quantidade <= 0:
            logging.warning("Quantidade inválida para retirada.")
            return False
        peca = self.db.obter_peca_por_id(peca_id)
        if not peca or peca.quantidade_disponivel < quantidade:
            logging.warning(f"Estoque insuficiente para peça {peca_id}: disponível {peca.quantidade_disponivel if peca else 0}")
            return False
        self.db.registrar_retirada_peca(usuario_id, peca_id, quantidade)
        logging.info(f"Retirada registrada: {quantidade} unidades da peça {peca_id} por usuário {usuario_id}")
        if quantidade > 10:
            self.adicionar_alerta(f"Retirada alta de {quantidade} unidades da peça {peca.nome} por {usuario_id}")
        return True

    def registrar_devolucao_peca(self, retirada_id: int, quantidade_devolvida: int) -> bool:
        if quantidade_devolvida < 0:
            logging.warning("Quantidade inválida para devolução.")
            return False
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT quantidade_retirada FROM retiradas_pecas WHERE id = ? AND status IN ("pendente", "parcial")',
            (retirada_id,)
        )
        result = cursor.fetchone()
        conn.close()
        if not result or quantidade_devolvida > result[0]:
            logging.warning(f"Devolução inválida para retirada {retirada_id}")
            return False
        self.db.registrar_devolucao_peca(retirada_id, quantidade_devolvida)
        logging.info(f"Devolução registrada: {quantidade_devolvida} unidades para retirada {retirada_id}")
        return True

    def obter_pecas_pendentes_usuario(self, usuario_id: str) -> List[RetiradaPeca]:
        return self.db.obter_retiradas_pendentes_usuario(usuario_id)

    def obter_retiradas_pendentes_usuario_por_peca(self, peca_id: int) -> List[RetiradaPeca]:
        return self.db.obter_retiradas_pendentes_por_peca(peca_id)