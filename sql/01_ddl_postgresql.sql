-- =============================================================================
-- PROYECTO DE INTELIGENCIA DE NEGOCIOS: LÍNEAS DE ENVASADO DE VINILOS Y TÉMPERAS
-- SCRIPT DDL DE CREACIÓN DE BASE DE DATOS Y MODELO DIMENSIONAL (KIMBALL)
-- MOTOR: PostgreSQL 15+ / MySQL Compatible (Sintaxis Estándar ANSI SQL)
-- GESTIONADO DESDE: DBeaver / Docker
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS bi_temperas;
SET search_path TO bi_temperas, public;

-- -----------------------------------------------------------------------------
-- 1. TABLAS DE DIMENSIONES (CONFORMADAS)
-- -----------------------------------------------------------------------------

-- 1.1 Dimensión Tiempo / Fecha
CREATE TABLE IF NOT EXISTS dim_fecha (
    fecha_key           INTEGER PRIMARY KEY, -- Formato YYYYMMDD (Ej: 20250328)
    fecha               DATE NOT NULL UNIQUE,
    anio                INTEGER NOT NULL,
    mes                 INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    nombre_mes          VARCHAR(20) NOT NULL,
    trimestre           INTEGER NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    semestre            INTEGER NOT NULL CHECK (semestre BETWEEN 1 AND 2),
    semana_anio         INTEGER NOT NULL CHECK (semana_anio BETWEEN 1 AND 53),
    dia_mes             INTEGER NOT NULL CHECK (dia_mes BETWEEN 1 AND 31),
    dia_semana          INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    nombre_dia          VARCHAR(20) NOT NULL,
    es_fin_de_semana    BOOLEAN NOT NULL,
    es_festivo          BOOLEAN DEFAULT FALSE
);

COMMENT ON TABLE dim_fecha IS 'Dimensión de tiempo para análisis de series temporales y cortes interanuales.';

-- 1.2 Dimensión Máquina
CREATE TABLE IF NOT EXISTS dim_maquina (
    maquina_key         SERIAL PRIMARY KEY,
    codigo_maquina      VARCHAR(50) NOT NULL UNIQUE, -- 'Vinilos_1', 'Vinilos_2', 'Vinilos_3', 'Vinilos_4'
    nombre_linea        VARCHAR(100) NOT NULL,
    tipo_tecnologia     VARCHAR(100) DEFAULT 'Envasadora Automática Rotativa',
    capacidad_diseno_u_min NUMERIC(6,2) DEFAULT 72.00,
    ubicacion_planta    VARCHAR(100) DEFAULT 'Planta Principal - Nave Envasado',
    estado_operativo    VARCHAR(50) DEFAULT 'Activa'
);

COMMENT ON TABLE dim_maquina IS 'Dimensión de líneas de envasado operativas en planta.';

-- 1.3 Dimensión Turno
CREATE TABLE IF NOT EXISTS dim_turno (
    turno_key           SERIAL PRIMARY KEY,
    codigo_turno        VARCHAR(50) NOT NULL UNIQUE, -- 'Turno 1', 'Turno 2', 'Turno 3', 'Especial 10.5h', etc.
    nombre_turno        VARCHAR(100) NOT NULL,
    hora_inicio         TIME,
    hora_fin            TIME,
    duracion_horas      NUMERIC(4,2) NOT NULL DEFAULT 8.00,
    tipo_jornada        VARCHAR(50) DEFAULT 'Rotativo'
);

COMMENT ON TABLE dim_turno IS 'Dimensión que estandariza los turnos de operación y sus horas reglamentarias.';

-- 1.4 Dimensión Operario
CREATE TABLE IF NOT EXISTS dim_operario (
    operario_key        SERIAL PRIMARY KEY,
    nombre_operario     VARCHAR(100) NOT NULL,
    cargo               VARCHAR(100) DEFAULT 'Operaria de Envasado',
    area_pertenencia    VARCHAR(100) DEFAULT 'Producción',
    activo              BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE dim_operario IS 'Dimensión de personal operario de las líneas de envasado.';

-- 1.5 Dimensión Referencia (Producto con SCD Tipo 2 para Bonificación)
CREATE TABLE IF NOT EXISTS dim_referencia (
    referencia_sk       SERIAL PRIMARY KEY, -- Llave subrogada técnica
    referencia_id       VARCHAR(100) NOT NULL, -- Llave de negocio / Natural (ej. 'Parchesitos 125 cc')
    nombre_referencia   VARCHAR(150) NOT NULL,
    tipo_producto       VARCHAR(50) NOT NULL, -- 'Vinilo', 'Témpera'
    presentacion_cc     VARCHAR(50),
    colores             INTEGER DEFAULT 6,
    unidades_display    INTEGER DEFAULT 36,
    display_paca        INTEGER DEFAULT 1,
    unidades_paca       INTEGER NOT NULL,
    velocidad_nominal_minuto NUMERIC(6,2) NOT NULL DEFAULT 72.00,
    
    -- Metadatos de SCD Tipo 2 (Slowly Changing Dimensions)
    fecha_inicio_validez DATE NOT NULL DEFAULT '2020-01-01',
    fecha_fin_validez    DATE NOT NULL DEFAULT '9999-12-31',
    es_registro_actual   BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE dim_referencia IS 'Dimensión de productos con SCD Tipo 2 para mantener la integridad histórica del OEE.';

-- 1.6 Dimensión Códigos y Jerarquía de Paros
CREATE TABLE IF NOT EXISTS dim_codigo_paro (
    codigo_paro_key     SERIAL PRIMARY KEY,
    area_impacto        VARCHAR(100) NOT NULL, -- Nivel 1: 'Mantenimiento', 'Producción', 'Calidad', 'Almacén', 'Programado'
    codigo_numero       INTEGER NOT NULL,       -- [1] al [18]
    codigo_paro_texto   VARCHAR(150) NOT NULL, -- Nivel 2: '[01] Falla del sistema electromecánico y/o de control'
    subcodigo           VARCHAR(50),           -- Nivel 3: '1.1', '1.2', '5.2'
    descripcion_subcodigo VARCHAR(200),        -- '1.1 FALLA MECANICA', '1.2 SISTEMA DE DOSIFICACIÓN'
    componente          VARCHAR(150),          -- Nivel 4: '1.1.A Banda', '1.1.B Motor', '1.1.C Sensor'
    tipo_paro           VARCHAR(50) NOT NULL DEFAULT 'No Programado' -- 'Programado' vs 'No Programado'
);

COMMENT ON TABLE dim_codigo_paro IS 'Jerarquía de paros en 4 niveles (Área -> Código -> Subcódigo -> Componente).';

-- 1.7 Dimensión Agente de Intervención / Personal Mantenimiento
CREATE TABLE IF NOT EXISTS dim_agente_intervencion (
    agente_key          SERIAL PRIMARY KEY,
    nombre_personal     VARCHAR(150) NOT NULL,
    area_rol            VARCHAR(100) NOT NULL DEFAULT 'Mantenimiento'
);

COMMENT ON TABLE dim_agente_intervencion IS 'Técnicos de mantenimiento y personal de apoyo que atiende los paros.';

-- 1.8 Dimensión Propia Construida: Severidad y Criticidad del Paro
CREATE TABLE IF NOT EXISTS dim_severidad_paro (
    severidad_key       SERIAL PRIMARY KEY,
    rango_duracion      VARCHAR(50) NOT NULL, -- '< 5 min', '5-15 min', '15-45 min', '> 45 min'
    nivel_severidad     VARCHAR(50) NOT NULL, -- 'Micro-paro', 'Paro Menor', 'Paro Significativo', 'Paro Crítico'
    es_alerta_grafana   BOOLEAN NOT NULL DEFAULT FALSE,
    protocolo_escalamiento VARCHAR(200) NOT NULL
);

COMMENT ON TABLE dim_severidad_paro IS 'Dimensión propia construida para categorizar la gravedad y disparar alertas en Grafana.';


-- -----------------------------------------------------------------------------
-- 2. TABLAS DE HECHOS (FACT TABLES)
-- -----------------------------------------------------------------------------

-- 2.1 Hechos de Producción por Turno
CREATE TABLE IF NOT EXISTS fact_produccion (
    produccion_id       BIGSERIAL PRIMARY KEY,
    fecha_key           INTEGER NOT NULL REFERENCES dim_fecha(fecha_key),
    maquina_key         INTEGER NOT NULL REFERENCES dim_maquina(maquina_key),
    turno_key           INTEGER NOT NULL REFERENCES dim_turno(turno_key),
    operario_key        INTEGER NOT NULL REFERENCES dim_operario(operario_key),
    referencia_sk       INTEGER NOT NULL REFERENCES dim_referencia(referencia_sk),
    
    -- Medidas base
    horas_trabajadas    NUMERIC(6,2) NOT NULL DEFAULT 0.00 CHECK (horas_trabajadas >= 0),
    horas_programadas   NUMERIC(6,2) NOT NULL DEFAULT 0.00 CHECK (horas_programadas >= 0),
    pacas_producidas    NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (pacas_producidas >= 0),
    unidades_reales     NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (unidades_reales >= 0),
    unidades_ideales    NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (unidades_ideales >= 0),
    tiempo_paro_horas   NUMERIC(6,2) NOT NULL DEFAULT 0.00 CHECK (tiempo_paro_horas >= 0),
    tiempo_operativo_horas NUMERIC(6,2) NOT NULL DEFAULT 0.00,
    
    -- Indicadores calculados a nivel de fila (OEE y componentes)
    disponibilidad_pct  NUMERIC(5,2) DEFAULT 0.00 CHECK (disponibilidad_pct BETWEEN 0 AND 100),
    rendimiento_pct     NUMERIC(5,2) DEFAULT 0.00 CHECK (rendimiento_pct >= 0),
    calidad_pct         NUMERIC(5,2) DEFAULT 100.00 CHECK (calidad_pct BETWEEN 0 AND 100),
    oee_pct             NUMERIC(5,2) DEFAULT 0.00 CHECK (oee_pct >= 0),
    
    -- Metadatos de auditoría
    fecha_carga         TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE fact_produccion IS 'Grano: 1 fila por turno de máquina envasadora, fecha y referencia procesada.';

-- 2.2 Hechos de Eventos de Paro
CREATE TABLE IF NOT EXISTS fact_paros (
    paro_id             BIGSERIAL PRIMARY KEY,
    produccion_id       BIGINT REFERENCES fact_produccion(produccion_id) ON DELETE SET NULL,
    fecha_key           INTEGER NOT NULL REFERENCES dim_fecha(fecha_key),
    maquina_key         INTEGER NOT NULL REFERENCES dim_maquina(maquina_key),
    turno_key           INTEGER NOT NULL REFERENCES dim_turno(turno_key),
    operario_key        INTEGER NOT NULL REFERENCES dim_operario(operario_key),
    referencia_sk       INTEGER NOT NULL REFERENCES dim_referencia(referencia_sk),
    codigo_paro_key     INTEGER NOT NULL REFERENCES dim_codigo_paro(codigo_paro_key),
    agente_key          INTEGER REFERENCES dim_agente_intervencion(agente_key),
    severidad_key       INTEGER REFERENCES dim_severidad_paro(severidad_key),
    
    -- Medidas
    duracion_horas      NUMERIC(6,3) NOT NULL CHECK (duracion_horas >= 0),
    duracion_minutos    NUMERIC(8,2) NOT NULL CHECK (duracion_minutos >= 0),
    costo_estimado_cop  NUMERIC(12,2) DEFAULT 0.00,
    
    -- Contexto
    observaciones       TEXT,
    fecha_registro      TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE fact_paros IS 'Grano: 1 fila por cada evento individual de paro reportado en la línea.';


-- -----------------------------------------------------------------------------
-- 3. ÍNDICES ANALÍTICOS (OPTIMIZACIÓN DE CONSULTAS Y POWER BI / GRAFANA)
-- -----------------------------------------------------------------------------

-- Índices en fact_produccion
CREATE INDEX IF NOT EXISTS idx_fact_prod_fecha ON fact_produccion(fecha_key);
CREATE INDEX IF NOT EXISTS idx_fact_prod_maquina ON fact_produccion(maquina_key);
CREATE INDEX IF NOT EXISTS idx_fact_prod_maq_fecha ON fact_produccion(maquina_key, fecha_key);
CREATE INDEX IF NOT EXISTS idx_fact_prod_turno ON fact_produccion(turno_key);
CREATE INDEX IF NOT EXISTS idx_fact_prod_referencia ON fact_produccion(referencia_sk);

-- Índices en fact_paros
CREATE INDEX IF NOT EXISTS idx_fact_paros_fecha ON fact_paros(fecha_key);
CREATE INDEX IF NOT EXISTS idx_fact_paros_maquina ON fact_paros(maquina_key);
CREATE INDEX IF NOT EXISTS idx_fact_paros_codigo ON fact_paros(codigo_paro_key);
CREATE INDEX IF NOT EXISTS idx_fact_paros_severidad ON fact_paros(severidad_key);
CREATE INDEX IF NOT EXISTS idx_fact_paros_maq_fecha ON fact_paros(maquina_key, fecha_key);
CREATE INDEX IF NOT EXISTS idx_fact_paros_registro ON fact_paros(fecha_registro DESC);

-- Índices en dimensiones para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_dim_fecha_anio_mes ON dim_fecha(anio, mes);
CREATE INDEX IF NOT EXISTS idx_dim_ref_natural ON dim_referencia(referencia_id, es_registro_actual);
