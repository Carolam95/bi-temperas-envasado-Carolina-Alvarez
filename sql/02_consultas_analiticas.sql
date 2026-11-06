-- =============================================================================
-- CONSULTAS SQL ANALÍTICAS AVANZADAS PARA INTELIGENCIA DE NEGOCIOS
-- INCLUYE: AGREGACIONES, FUNCIONES DE VENTANA (WINDOW FUNCTIONS) Y COMPARATIVOS
-- MOTOR: PostgreSQL / Compatible ANSI SQL
-- =============================================================================

SET search_path TO bi_temperas, public;

-- -----------------------------------------------------------------------------
-- CONSULTA 1: COMPARATIVO INTERANUAL DE PRODUCCIÓN (2024 VS 2025) MES A MES
-- Pregunta de Negocio: ¿Cómo evolucionó la producción de pacas mes a mes entre 2024 y 2025?
-- Utiliza: Agregaciones, JOINs y funciones de pivote/agregación condicional con LAG()
-- -----------------------------------------------------------------------------
WITH produccion_mensual AS (
    SELECT 
        df.anio,
        df.mes,
        df.nombre_mes,
        dm.codigo_maquina,
        SUM(fp.pacas_producidas) AS total_pacas,
        SUM(fp.horas_trabajadas) AS total_horas_trabajadas,
        ROUND(AVG(fp.oee_pct), 2) AS oee_promedio
    FROM fact_produccion fp
    JOIN dim_fecha df ON fp.fecha_key = df.fecha_key
    JOIN dim_maquina dm ON fp.maquina_key = dm.maquina_key
    WHERE df.anio IN (2024, 2025)
    GROUP BY df.anio, df.mes, df.nombre_mes, dm.codigo_maquina
),
comparativo_periodos AS (
    SELECT 
        mes,
        nombre_mes,
        codigo_maquina,
        MAX(CASE WHEN anio = 2024 THEN total_pacas ELSE 0 END) AS pacas_2024,
        MAX(CASE WHEN anio = 2025 THEN total_pacas ELSE 0 END) AS pacas_2025,
        MAX(CASE WHEN anio = 2024 THEN oee_promedio ELSE 0 END) AS oee_2024,
        MAX(CASE WHEN anio = 2025 THEN oee_promedio ELSE 0 END) AS oee_2025
    FROM produccion_mensual
    GROUP BY mes, nombre_mes, codigo_maquina
)
SELECT 
    nombre_mes,
    codigo_maquina,
    pacas_2024,
    pacas_2025,
    (pacas_2025 - pacas_2024) AS variacion_absoluta_pacas,
    ROUND(
        CASE 
            WHEN pacas_2024 > 0 THEN ((pacas_2025 - pacas_2024) * 100.0 / pacas_2024)
            ELSE NULL 
        END, 2
    ) AS variacion_pct_pacas,
    oee_2024,
    oee_2025,
    ROUND((oee_2025 - oee_2024), 2) AS delta_oee_puntos_pct
FROM comparativo_periodos
ORDER BY mes, codigo_maquina;


-- -----------------------------------------------------------------------------
-- CONSULTA 2: OEE CONSOLIDADO Y DESGLOSE (DISPONIBILIDAD, RENDIMIENTO, CALIDAD)
-- Pregunta de Negocio: ¿Cuál es el OEE de cada máquina y qué componente penaliza más la línea?
-- Utiliza: Agregaciones matemáticas ponderadas para evitar el sesgo de promediar porcentajes
-- -----------------------------------------------------------------------------
SELECT 
    dm.codigo_maquina,
    df.anio,
    ROUND(SUM(fp.horas_trabajadas), 2) AS horas_trabajadas,
    ROUND(SUM(fp.tiempo_paro_horas), 2) AS horas_paro,
    ROUND(SUM(fp.tiempo_operativo_horas), 2) AS horas_operativas,
    ROUND(SUM(fp.unidades_reales), 0) AS unidades_reales,
    ROUND(SUM(fp.unidades_ideales), 0) AS unidades_nominales,
    
    -- Disponibilidad Ponderada = Horas Operativas / Horas Trabajadas
    ROUND(
        CASE WHEN SUM(fp.horas_trabajadas) > 0 
             THEN (SUM(fp.tiempo_operativo_horas) * 100.0 / SUM(fp.horas_trabajadas)) 
             ELSE 0 END, 2
    ) AS disponibilidad_pct,
    
    -- Rendimiento Ponderado = Unidades Reales / Unidades Ideales
    ROUND(
        CASE WHEN SUM(fp.unidades_ideales) > 0 
             THEN (SUM(fp.unidades_reales) * 100.0 / SUM(fp.unidades_ideales)) 
             ELSE 0 END, 2
    ) AS rendimiento_pct,
    
    -- Calidad Ponderada (Estimada)
    ROUND(AVG(fp.calidad_pct), 2) AS calidad_pct,
    
    -- OEE Ponderado
    ROUND(
        (
            CASE WHEN SUM(fp.horas_trabajadas) > 0 THEN (SUM(fp.tiempo_operativo_horas) / SUM(fp.horas_trabajadas)) ELSE 0 END
            *
            CASE WHEN SUM(fp.unidades_ideales) > 0 THEN (SUM(fp.unidades_reales) / SUM(fp.unidades_ideales)) ELSE 0 END
            *
            (AVG(fp.calidad_pct) / 100.0)
        ) * 100.0, 2
    ) AS oee_ponderado_pct
FROM fact_produccion fp
JOIN dim_maquina dm ON fp.maquina_key = dm.maquina_key
JOIN dim_fecha df ON fp.fecha_key = df.fecha_key
WHERE df.anio >= 2024
GROUP BY dm.codigo_maquina, df.anio
ORDER BY dm.codigo_maquina, df.anio;


-- -----------------------------------------------------------------------------
-- CONSULTA 3: ANÁLISIS DE PARETO DE CAUSAS DE PARO (80 / 20)
-- Pregunta de Negocio: ¿Cuáles son los paros que acumulan el 80% de las horas perdidas?
-- Utiliza: FUNCIONES DE VENTANA (SUM() OVER() y ROW_NUMBER() OVER())
-- -----------------------------------------------------------------------------
WITH resumen_paros AS (
    SELECT 
        dcp.area_impacto,
        dcp.codigo_numero,
        dcp.codigo_paro_texto,
        SUM(fpar.duracion_horas) AS horas_paro,
        COUNT(fpar.paro_id) AS cantidad_eventos
    FROM fact_paros fpar
    JOIN dim_codigo_paro dcp ON fpar.codigo_paro_key = dcp.codigo_paro_key
    GROUP BY dcp.area_impacto, dcp.codigo_numero, dcp.codigo_paro_texto
),
pareto_calculo AS (
    SELECT 
        area_impacto,
        codigo_numero,
        codigo_paro_texto,
        ROUND(horas_paro, 2) AS horas_paro,
        cantidad_eventos,
        ROUND(
            (horas_paro * 100.0 / SUM(horas_paro) OVER ()), 2
        ) AS pct_individual,
        ROUND(
            SUM(horas_paro) OVER (ORDER BY horas_paro DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) 
            * 100.0 / SUM(horas_paro) OVER (), 2
        ) AS pct_acumulado_pareto,
        ROW_NUMBER() OVER (ORDER BY horas_paro DESC) AS ranking
    FROM resumen_paros
)
SELECT 
    ranking,
    area_impacto,
    codigo_paro_texto,
    horas_paro,
    cantidad_eventos,
    pct_individual,
    pct_acumulado_pareto,
    CASE 
        WHEN pct_acumulado_pareto <= 80.0 THEN 'Zona Vital (80% Pareto)'
        ELSE 'Zona Trivial'
    END AS clasificacion_gestion
FROM pareto_calculo
ORDER BY ranking;


-- -----------------------------------------------------------------------------
-- CONSULTA 4: MTTR (TIEMPO MEDIO DE REPARACIÓN) POR COMPONENTE ELECTROMECÁNICO
-- Pregunta de Negocio: ¿Qué componentes de la falla 01 tardan más en repararse?
-- Utiliza: Filtros por jerarquía, RANK() OVER() y promedios de duración
-- -----------------------------------------------------------------------------
SELECT 
    dcp.subcodigo,
    dcp.descripcion_subcodigo,
    COALESCE(dcp.componente, 'General') AS componente,
    COUNT(fpar.paro_id) AS total_fallas,
    ROUND(SUM(fpar.duracion_horas), 2) AS total_horas_inactividad,
    ROUND(AVG(fpar.duracion_minutos), 1) AS mttr_minutos_promedio,
    DENSE_RANK() OVER (ORDER BY SUM(fpar.duracion_horas) DESC) AS rank_impacto_horas
FROM fact_paros fpar
JOIN dim_codigo_paro dcp ON fpar.codigo_paro_key = dcp.codigo_paro_key
WHERE dcp.codigo_numero = 1 -- [01] Falla Electromecánica
GROUP BY dcp.subcodigo, dcp.descripcion_subcodigo, dcp.componente
ORDER BY total_horas_inactividad DESC;


-- -----------------------------------------------------------------------------
-- CONSULTA 5: MONITOREO NEAR REAL-TIME PARA GRAFANA (ESTADO ACTUAL Y ALERTAS)
-- Pregunta de Negocio: Estado de las últimas 24 horas y detección de alertas críticas
-- Utiliza: Window functions LEAD/LAG, filtrado dinámico para dashboards operativos
-- -----------------------------------------------------------------------------
SELECT 
    dm.codigo_maquina,
    COUNT(fpar.paro_id) AS total_paros_recientes,
    ROUND(SUM(fpar.duracion_horas), 2) AS horas_paradas_recientes,
    ROUND(AVG(fpar.duracion_minutos), 1) AS duracion_promedio_minutos,
    MAX(fpar.fecha_registro) AS ultimo_evento_registrado,
    SUM(CASE WHEN dsp.es_alerta_grafana = TRUE THEN 1 ELSE 0 END) AS conteo_alertas_criticas,
    CASE 
        WHEN SUM(CASE WHEN dsp.es_alerta_grafana = TRUE THEN 1 ELSE 0 END) > 0 THEN 'ESTADO CRÍTICO (ALERTA ACTIVA)'
        WHEN SUM(fpar.duracion_horas) > 2.0 THEN 'ATENCIÓN REQUERIDA'
        ELSE 'OPERACIÓN NORMAL'
    END AS semaforo_operativo
FROM fact_paros fpar
JOIN dim_maquina dm ON fpar.maquina_key = dm.maquina_key
LEFT JOIN dim_severidad_paro dsp ON fpar.severidad_key = dsp.severidad_key
GROUP BY dm.codigo_maquina
ORDER BY horas_paradas_recientes DESC;
