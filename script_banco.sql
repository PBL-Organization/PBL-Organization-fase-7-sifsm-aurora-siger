-- ============================================================
-- SIFSM - Sistema Integrado de Futuro Sustentável em Marte
-- Arquivo: script_banco.sql
-- Descrição: Estrutura DDL para persistência dos Módulos da Aurora Siger
-- ============================================================

CREATE TABLE IF NOT EXISTS modulos_colonia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_modulo TEXT NOT NULL UNIQUE,
    nome_modulo TEXT NOT NULL,
    tipo_modulo TEXT NOT NULL, -- Ex: Habitação, Estufa, Energia, Laboratório
    nivel_critico INTEGER NOT NULL, -- 1: Baixo, 2: Médio, 3: Crítico
    consumo_kwh REAL NOT NULL DEFAULT 0.0,
    temperatura_c REAL NOT NULL DEFAULT 20.0,
    status_operacional TEXT NOT NULL DEFAULT 'OPERACIONAL', -- OPERACIONAL, ALERTA, MANUTENCAO
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Registros iniciais para simulação
INSERT OR IGNORE INTO modulos_colonia 
(codigo_modulo, nome_modulo, tipo_modulo, nivel_critico, consumo_kwh, temperatura_c, status_operacional) 
VALUES 
('MOD-HAB-01', 'Habitação Alpha', 'Habitação', 3, 145.5, 22.4, 'OPERACIONAL'),
('MOD-AGR-01', 'Estufa Hidropônica 1', 'Agricultura', 2, 88.0, 26.1, 'OPERACIONAL'),
('MOD-ENG-01', 'Matriz Solar Principal', 'Energia', 3, 310.2, 45.0, 'ALERTA'),
('MOD-LAB-01', 'Laboratório de Pesquisa', 'Laboratório', 1, 62.4, 19.8, 'OPERACIONAL');