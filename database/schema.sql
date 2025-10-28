-- -----------------------------------------------------
-- Criação do banco de dados
-- -----------------------------------------------------
CREATE DATABASE IF NOT EXISTS `carrinho` 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;
USE `carrinho`;

-- -----------------------------------------------------
-- Tabela: carrinhos
-- -----------------------------------------------------
DROP TABLE IF EXISTS `carrinhos`;
CREATE TABLE `carrinhos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Tabela: usuarios
-- -----------------------------------------------------
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `cargo` VARCHAR(100),
  `perfil` VARCHAR(50),
  `ativo` TINYINT(1) DEFAULT 1,
  `data_cadastro` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Tabela: carrinhos_has_usuarios
-- -----------------------------------------------------
DROP TABLE IF EXISTS `carrinhos_has_usuarios`;
CREATE TABLE `carrinhos_has_usuarios` (
  `carrinhos_id` INT NOT NULL,
  `usuarios_id` INT NOT NULL,
  `cargo` VARCHAR(50),
  `nome` VARCHAR(100),
  PRIMARY KEY (`carrinhos_id`, `usuarios_id`),
  CONSTRAINT `fk_carrinhos_has_usuarios_carrinhos`
    FOREIGN KEY (`carrinhos_id`) REFERENCES `carrinhos` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_carrinhos_has_usuarios_usuarios`
    FOREIGN KEY (`usuarios_id`) REFERENCES `usuarios` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Tabela: pecas
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pecas`;
CREATE TABLE `pecas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `descricao` TEXT,
  `categoria` VARCHAR(100),
  `quantidade` INT DEFAULT 0,
  `tipo` VARCHAR(50),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Tabela: gavetas
-- -----------------------------------------------------
DROP TABLE IF EXISTS `gavetas`;
CREATE TABLE `gavetas` (
  `carrinhos_id` INT NOT NULL,
  `pecas_id` INT NOT NULL,
  `descricao` VARCHAR(255),
  PRIMARY KEY (`carrinhos_id`, `pecas_id`),
  CONSTRAINT `fk_gavetas_carrinhos`
    FOREIGN KEY (`carrinhos_id`) REFERENCES `carrinhos` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_gavetas_pecas`
    FOREIGN KEY (`pecas_id`) REFERENCES `pecas` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Tabela: eventos
-- -----------------------------------------------------
DROP TABLE IF EXISTS `eventos`;
CREATE TABLE `eventos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `acao` VARCHAR(100),
  `gaveta_id` INT,
  `usuario_id` INT,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `sucesso` TINYINT(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `fk_eventos_gavetas`
    FOREIGN KEY (`gaveta_id`) REFERENCES `gavetas` (`pecas_id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_eventos_usuarios`
    FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Tabela: retiradas_pecas
-- -----------------------------------------------------
DROP TABLE IF EXISTS `retiradas_pecas`;
CREATE TABLE `retiradas_pecas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `peca_id` INT NOT NULL,
  `usuario_id` INT,
  `quantidade_retirada` INT NOT NULL,
  `quantidade_devolvida` INT DEFAULT 0,
  `status` ENUM('pendente', 'concluída') DEFAULT 'pendente',
  `timestamp_retirada` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `timestamp_devolucao` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `peca_id` (`peca_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `fk_retiradas_pecas_pecas`
    FOREIGN KEY (`peca_id`) REFERENCES `pecas` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_retiradas_pecas_usuarios`
    FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
