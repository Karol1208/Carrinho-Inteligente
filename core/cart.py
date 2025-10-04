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
from hardware.simulator import SimuladorHardware



class CarrinhoInteligenteAvancado:
    def __init__(self, db_path: str = 'carrinho.db'):
        self.db = DatabaseManager(db_path=db_path)
        self.hardware = SimuladorHardware()
        self.gavetas = {i: GavetaAvancada(i, f"Gaveta {i}") for i in range(1, 6)}
        self.sistema_ativo = True
        self.modo_manutencao = False
        self.alertas_ativos = []


        self.monitor_thread = threading.Thread(target=self.monitor_sistema, daemon=True)
        self.monitor_thread.start()


    def validar_cartao(self, codigo_cartao: str) -> Optional[UsuarioCartao]:
        if not codigo_cartao:
            return None
        usuario = self.db.obter_usuario(codigo_cartao)
        if usuario:
            logging.info(f"Cartão validado: {usuario.nome} ({usuario.id})")
        else:
            logging.warning(f"Cartão inválido/não autorizado: {codigo_cartao}")
        return usuario


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
            logging.info(f"Gaveta {gaveta_id} já está aberta ou bloqueada, não pode abrir novamente.")
        evento = EventoGaveta(
            gaveta_id=gaveta_id,
            usuario_id=usuario.id if usuario else codigo_cartao,
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


    def monitor_sistema(self):
        while self.sistema_ativo:
            try:
                for gaveta_id, gaveta in self.gavetas.items():
                    if gaveta.aberta:
                        tempo_aberta = gaveta.tempo_aberta()
                        if tempo_aberta > 600:  # 10 minutos
                            usuario = self.db.obter_usuario(gaveta.usuario_atual) if gaveta.usuario_atual else None
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


                self.verificar_status_hardware()
                time.sleep(10)  # Verifica a cada 10 segundos
            except Exception as e:
                logging.error(f"Erro no monitor do sistema: {e}")


    def verificar_status_hardware(self):
        for gaveta_id in self.gavetas:
            hardware_aberta = self.hardware.gaveta_esta_aberta(gaveta_id)
            software_aberta = self.gavetas[gaveta_id].aberta
            if hardware_aberta != software_aberta:
                self.adicionar_alerta(f"Inconsistência detectada na gaveta {gaveta_id}")
                logging.warning(f"Status inconsistente - Gaveta {gaveta_id}: HW={hardware_aberta}, SW={software_aberta}")


    def adicionar_alerta(self, mensagem: str):
        alerta = {'mensagem': mensagem, 'timestamp': datetime.datetime.now().isoformat()}
        self.alertas_ativos.append(alerta)
        if len(self.alertas_ativos) > 20:
            self.alertas_ativos.pop(0)


    def listar_pecas_por_gaveta(self, gaveta_id: int) -> List[Peca]:
        return self.db.listar_pecas_por_gaveta(gaveta_id)


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
        cursor.execute('SELECT quantidade_retirada FROM retiradas_pecas WHERE id = ? AND status IN ("pendente", "parcial")', (retirada_id,))
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


    def listar_todas_pecas(self) -> List[Peca]:
        return self.db.listar_todas_pecas()


    def adicionar_peca(self, peca: Peca) -> bool:
        if peca.quantidade_disponivel < 0:
            logging.warning("Quantidade inválida para peça.")
            return False
        self.db.adicionar_peca(peca)
        logging.info(f"Peça adicionada/atualizada: {peca.nome} na Gaveta {peca.gaveta_id}")
        return True
    
    
    def obter_retiradas_pendentes_usuario_por_peca(self, peca_id: int) -> List[RetiradaPeca]:
        return self.db.obter_retiradas_pendentes_por_peca(peca_id)
    

    def abrir_todas_gavetas_manutencao(self, usuario_id: str) -> bool:
        """Abre todas as gavetas, bypassando a regra de uma por vez. Requer admin."""
        usuario = self.db.obter_usuario(usuario_id)
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
                        gaveta_id=gaveta_id, usuario_id=usuario.id, acao='abrir_admin',
                        timestamp=datetime.datetime.now().isoformat(), sucesso=True
                    ))
                else:
                    sucesso_total = False
        return sucesso_total