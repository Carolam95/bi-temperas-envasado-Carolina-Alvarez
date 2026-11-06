import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\USUARIO\.gemini\antigravity\scratch\proyecto-bi-temperas\data\processed\bi_temperas.db"
conn = sqlite3.connect(DB_PATH)

print("=" * 60)
print("TESTING SQL ANALYTICAL QUERIES ON PROCESSED DATABASE")
print("=" * 60)

# Query 1: Comparativo Interanual
q1 = """
WITH prod_mensual AS (
    SELECT 
        df.anio,
        df.mes,
        df.nombre_mes,
        dm.codigo_maquina,
        SUM(fp.pacas_producidas) AS total_pacas,
        ROUND(AVG(fp.oee_pct), 2) AS oee_promedio
    FROM fact_produccion fp
    JOIN dim_fecha df ON fp.fecha_key = df.fecha_key
    JOIN dim_maquina dm ON fp.maquina_key = dm.maquina_key
    WHERE df.anio IN (2024, 2025)
    GROUP BY df.anio, df.mes, df.nombre_mes, dm.codigo_maquina
)
SELECT 
    nombre_mes,
    codigo_maquina,
    MAX(CASE WHEN anio = 2024 THEN total_pacas ELSE 0 END) AS pacas_2024,
    MAX(CASE WHEN anio = 2025 THEN total_pacas ELSE 0 END) AS pacas_2025,
    MAX(CASE WHEN anio = 2024 THEN oee_promedio ELSE 0 END) AS oee_2024,
    MAX(CASE WHEN anio = 2025 THEN oee_promedio ELSE 0 END) AS oee_2025
FROM prod_mensual
GROUP BY mes, nombre_mes, codigo_maquina
ORDER BY mes, codigo_maquina
LIMIT 8;
"""
print("\n--- Consulta 1: Comparativo 2024 vs 2025 (Sample) ---")
print(pd.read_sql_query(q1, conn))

# Query 2: Pareto de Paros (80/20)
q2 = """
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
pareto AS (
    SELECT 
        area_impacto,
        codigo_numero,
        codigo_paro_texto,
        ROUND(horas_paro, 2) AS horas_paro,
        cantidad_eventos,
        ROUND((horas_paro * 100.0 / (SELECT SUM(duracion_horas) FROM fact_paros)), 2) AS pct_individual,
        ROUND(SUM(horas_paro) OVER (ORDER BY horas_paro DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) 
              * 100.0 / (SELECT SUM(duracion_horas) FROM fact_paros), 2) AS pct_acumulado,
        ROW_NUMBER() OVER (ORDER BY horas_paro DESC) AS ranking
    FROM resumen_paros
)
SELECT ranking, codigo_paro_texto, horas_paro, cantidad_eventos, pct_individual, pct_acumulado,
       CASE WHEN pct_acumulado <= 80.0 THEN 'Zona Vital (80% Pareto)' ELSE 'Zona Trivial' END AS clasificacion
FROM pareto
ORDER BY ranking
LIMIT 8;
"""
print("\n--- Consulta 2: Pareto de Paros (Top 8 Causas) ---")
print(pd.read_sql_query(q2, conn))

# Query 3: MTTR por Componente en Código 01
q3 = """
SELECT 
    dcp.subcodigo,
    dcp.descripcion_subcodigo,
    COUNT(fpar.paro_id) AS total_fallas,
    ROUND(SUM(fpar.duracion_horas), 2) AS total_horas_inactividad,
    ROUND(AVG(fpar.duracion_minutos), 1) AS mttr_minutos_promedio,
    DENSE_RANK() OVER (ORDER BY SUM(fpar.duracion_horas) DESC) AS ranking_impacto
FROM fact_paros fpar
JOIN dim_codigo_paro dcp ON fpar.codigo_paro_key = dcp.codigo_paro_key
WHERE dcp.codigo_numero = 1
GROUP BY dcp.subcodigo, dcp.descripcion_subcodigo
ORDER BY total_horas_inactividad DESC
LIMIT 6;
"""
print("\n--- Consulta 3: MTTR Código 01 Fallas Electromecánicas ---")
print(pd.read_sql_query(q3, conn))

conn.close()
