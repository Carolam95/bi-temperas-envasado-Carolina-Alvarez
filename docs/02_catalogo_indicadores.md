# Catálogo de Indicadores y Métricas Operativas
**Proyecto de Inteligencia de Negocios End-to-End**

---

## 1. Indicadores Actuales (Procedimiento P-MTO-22)

Los indicadores que el procedimiento vigente reporta en tablas dinámicas y comités mensuales son:

1. **Producción General (%):**
   * Relación entre la producción real en pacas y la meta establecida por turno.
2. **Producción por Máquina (Comparativo Interanual 2024 vs 2025):**
   * Comparación mes a mes del volumen de pacas y tasa de productividad entre años fiscales consecutivos.
3. **Porcentaje de Códigos de Paro por Máquina (%):**
   * Participación porcentual de las horas de cada código de paro ([01] al [18]) sobre el total de horas de paro registradas.
4. **Análisis Detallado de Códigos Críticos (01, 03 y 05):**
   * Desglose jerárquico a nivel de subcódigo y componente para:
     * `Código 01`: Fallas electromecánicas y control (Banda, Motor, Sensor, Dosificación, etc.).
     * `Código 03`: Novedades energéticas (Subestación, Red pública, Aire comprimido, Vapor).
     * `Código 05`: Ajustes operativos y personal involucrado (Operarios vs Mantenimiento).

---

## 2. Indicadores Propuestos (Que el Excel NO Calcula) y Justificación

| Indicador Propuesto | Justificación de Negocio |
| :--- | :--- |
| **OEE (Overall Equipment Effectiveness / Eficiencia Global de Equipos)** | Estándar mundial en manufactura (ISO 22400 / SEMI E10). Permite a la gerencia evaluar la verdadera productividad integrando tres pérdidas fundamentales: tiempo (disponibilidad), velocidad (rendimiento) y defectos (calidad). |
| **Disponibilidad Operativa ($A$)** | Discrimina el tiempo que la máquina estuvo efectivamente funcionando frente al tiempo planificado, separando paros programados de fallas imprevistas. |
| **Rendimiento / Eficiencia de Desempeño ($P$)** | Mide si las líneas operan a su velocidad nominal diseñada (ej. 72 u/min) o si sufren micro-paros y reducción de velocidad que el Excel actual oculta. |
| **Tasa de Calidad ($Q$)** | Cuantifica las unidades no conformes, mermas por derrame (Código 06) o rechazos por microbiología (Código 13). |
| **MTBF (Mean Time Between Failures / Tiempo Medio Entre Fallas)** | Indicador vital de confiabilidad para el Jefe de Mantenimiento. Mide el tiempo promedio de operación continua entre fallas electromecánicas (Código 01). |
| **MTTR (Mean Time To Repair / Tiempo Medio de Reparación)** | Indicador de mantenibilidad y capacidad de respuesta del equipo técnico. Mide el tiempo promedio transcurrido desde que ocurre una avería hasta su puesta a punto. |
| **Costo Estimado de Inactividad (Cost of Downtime)** | Asocia un costo financiero por hora muerta según el estándar de la línea para sustentar presupuestos de CAPEX y modernización. |

---

## 3. Matriz del Catálogo de Indicadores

| Nombre del Indicador | Fórmula Matemática | Unidad | Granularidad | Meta / Umbral | Fuente de Datos | Usuario Consumidor |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OEE Global** | $\text{OEE} = A \times P \times Q$ | Porcentaje (%) | Máquina, Día, Mes, Año | $\ge 85\%$ (Clase Mundial) / Alerta $<75\%$ | `fact_produccion`, `fact_paros` | Gerencia General, Dirección de Operaciones |
| **Disponibilidad ($A$)** | $\frac{\text{Horas Operativas Reales}}{\text{Horas Programadas}}$ | Porcentaje (%) | Máquina, Turno, Día | $\ge 90\%$ / Alerta $<80\%$ | `fact_produccion`, `fact_paros` | Supervisor de Turno, Mantenimiento |
| **Rendimiento ($P$)** | $\frac{\text{Unidades Reales Producidas}}{\text{Horas Operativas} \times \text{Velocidad Nominal}}$ | Porcentaje (%) | Máquina, Turno, Referencia | $\ge 95\%$ / Alerta $<85\%$ | `fact_produccion`, `dim_referencia` | Supervisor de Producción, Mantenimiento |
| **Tasa de Calidad ($Q$)** | $\frac{\text{Unidades Conformes}}{\text{Unidades Totales Producidas}}$ | Porcentaje (%) | Máquina, Lote, Referencia | $\ge 99.5\%$ / Alerta $<98\%$ | `fact_produccion`, `fact_paros` | Líder de Calidad, Gerencia |
| **MTBF (Confiabilidad)** | $\frac{\sum \text{Horas Operativas}}{\text{Número de Eventos Falla (Cód. 01)}}$ | Horas / Falla | Máquina, Mes | $\ge 120 \text{ hrs}$ | `fact_paros`, `fact_produccion` | Coordinador de Mantenimiento |
| **MTTR (Mantenibilidad)** | $\frac{\sum \text{Horas Paro Falla (Cód. 01)}}{\text{Número de Eventos Falla (Cód. 01)}}$ | Horas / Reparación | Máquina, Mes | $\le 1.5 \text{ hrs}$ | `fact_paros` | Coordinador de Mantenimiento |
| **Producción Total (Pacas)** | $\sum \text{Pacas Producidas}$ | Pacas | Máquina, Turno, Día, Mes | Meta mensual según plan maestro | `fact_produccion` | Alta Dirección, Planeación |
| **Tiempo Total de Paro** | $\sum \text{Duración Paro (Horas)}$ | Horas | Máquina, Turno, Cód. Paro | Reducción interanual de 15% | `fact_paros` | Mantenimiento, Supervisores |
| **Índice de Paros No Programados** | $\frac{\sum \text{Horas Paro No Programado}}{\sum \text{Horas Paro Total}}$ | Porcentaje (%) | Máquina, Mes | $\le 30\%$ | `fact_paros`, `dim_codigo_paro` | Mantenimiento, Dirección de Planta |
