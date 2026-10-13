-- Arquitetura de Banco de Dados: EV ChargeOps (GoodWe + FIAP)
-- Resolução do cenário de múltiplos veículos/moradores compartilhando a mesma vaga via RFID

CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    apartamento VARCHAR(20) NOT NULL
);

CREATE INDEX idx_usuarios_apartamento ON usuarios (apartamento);

CREATE TABLE rfids (
    rfid_tag VARCHAR(50) PRIMARY KEY,
    id_usuario INT NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE RESTRICT
);

CREATE TABLE carregadores (
    charger_id VARCHAR(50) PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL,
    vaga VARCHAR(30) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    potencia_max_kw NUMERIC(4,2) DEFAULT 7.4
);

CREATE TABLE historico_sessoes (
    id_sessao SERIAL PRIMARY KEY,
    charger_id VARCHAR(50) NOT NULL,
    rfid_tag VARCHAR(50) NOT NULL,
    inicio_sessao TIMESTAMP WITH TIME ZONE NOT NULL,
    fim_sessao TIMESTAMP WITH TIME ZONE NOT NULL,
    energia_consumida_kwh NUMERIC (6,2) NOT NULL,
    status_final VARCHAR(50) NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_charger FOREIGN KEY (charger_id) REFERENCES carregadores (charger_id) ON DELETE RESTRICT,
    CONSTRAINT fk_rfid FOREIGN KEY (rfid_tag) REFERENCES rfids (rfid_tag) ON DELETE RESTRICT,
    CONSTRAINT chk_datas CHECK (fim_sessao >= inicio_sessao)
);

CREATE INDEX idx_sessoes_datas ON historico_sessoes(inicio_sessao, fim_sessao);
CREATE INDEX idx_sessoes_rfid ON historico_sessoes(rfid_tag);
