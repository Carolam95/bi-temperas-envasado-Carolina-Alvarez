# Reporte de Auditoría y Reconciliación ETL
**Fecha de Ejecución:** 2026-11-06 00:07:03

## 1. Métricas de Reconciliación

| Métrica | Fuente Original (Excel .xlsm) | Modelo Dimensional (PostgreSQL) | Diferencia Absoluta | Estado de Cuadre |
| :--- | :--- | :--- | :--- | :--- |
| **Pacas Producidas** | 378,778.00 | 378,778.00 | 0.00 | **100% Cuadrado** |
| **Horas Trabajadas** | 38,063.35 hrs | 38,063.35 hrs | 0.00 hrs | **100% Cuadrado** |
| **Horas de Paro Totales** | 8,449.65 hrs | 8,449.65 hrs | -0.00 hrs | **100% Cuadrado** |

## 2. Conteos de Entidades Transformadas
* **Filas crudas en Excel:** 8,208
* **Turnos en `fact_produccion`:** 4,759
* **Eventos en `fact_paros`:** 16,532
* **Dimensiones conformadas:**
  * `dim_fecha`: 1,183 días
  * `dim_maquina`: 4 máquinas
  * `dim_turno`: 7 turnos
  * `dim_operario`: 34 operarias
  * `dim_referencia`: 65 referencias (SCD Tipo 2)
  * `dim_codigo_paro`: 84 códigos y subcódigos
  * `dim_severidad_paro`: 4 niveles de severidad
  * `dim_agente_intervencion`: 39 técnicos y agentes
