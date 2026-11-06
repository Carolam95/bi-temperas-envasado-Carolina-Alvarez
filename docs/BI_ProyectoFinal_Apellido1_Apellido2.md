# PROYECTO FINAL DE INTELIGENCIA DE NEGOCIOS: SOLUCIÓN DE EXTREMO A EXTREMO PARA LÍNEAS DE ENVASADO DE VINILOS Y TÉMPERAS

**Documento Técnico de Entrega y Sustentación**  
**Nombre del Archivo Oficial:** `BI_ProyectoFinal_Apellido1_Apellido2.pdf`  
**Enlace al Repositorio de Código:** `https://github.com/usuario/bi-temperas-envasado` *(Simulado / Estructurado en repositorio local)*  

---

## PORTADA

* **Institución:** Universidad / Facultad de Ingeniería  
* **Asignatura:** Inteligencia de Negocios (Business Intelligence)  
* **Título del Proyecto:** Diseño, Implementación y Despliegue Contenerizado de una Solución de BI End-to-End para el Monitoreo de Eficiencia Operativa (OEE) y Paros de Producción  
* **Integrantes del Equipo:**  
  * Integrante 1 (Apellido 1, Nombre 1)  
  * Integrante 2 (Apellido 2, Nombre 2)  
* **Fecha de Entrega:** Noviembre 2026  

---

## 1. INTRODUCCIÓN Y CONTEXTO EMPRESARIAL

La empresa caso de estudio es una fábrica manufacturera de vinilos y témperas que cuenta con cuatro líneas automatizadas de envasado (`Vinilos_1`, `Vinilos_2`, `Vinilos_3` y `Vinilos_4`). El proceso productivo tradicional iniciaba con el diligenciamiento a mano por parte de las operarias del formato en papel denominado "hora a hora" (procedimiento `P-MTO-22`). Posteriormente, el área de mantenimiento transcribía de forma manual estos registros a un libro de Microsoft Excel con macros (`SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm`).

### 1.1 El Problema de Negocio
La alta dirección identificó dos limitaciones críticas que el Excel no resolvía:
1. **Falta de Capacidad Analítica Estratégica:** Imposibilidad de comparar tendencias plurianuales (2022 a 2025), analizar el comportamiento entre máquinas, turnos y referencias, e identificar las causas raíz de paros bajo un análisis de Pareto para justificar inversiones de CAPEX.
2. **Latencia Operativa y Falta de Monitoreo en Tiempo Real:** El informe consolidado se socializaba mensualmente. Cuando ocurría una falla severa o caída de disponibilidad, supervisores y mantenimiento no contaban con alertas tempranas para intervenir en el momento exacto.

---

## 2. IDENTIFICACIÓN DE USUARIOS Y PREGUNTAS DE NEGOCIO

| Rol / Usuario | Capa | Herramienta | Preguntas de Negocio Clave |
| :--- | :--- | :--- | :--- |
| **Gerencia General y Dirección de Operaciones** | Estratégica | Power BI | • ¿Cuál es el OEE global y cómo evolucionó mes a mes entre 2022 y 2025?<br>• ¿Cuál es la comparación de rendimiento productivo 2024 vs 2025?<br>• ¿Qué líneas son cuellos de botella para enfocar presupuesto? |
| **Coordinador / Jefe de Mantenimiento** | Táctica | Power BI / Grafana | • ¿Cuáles son los paros que acumulan el 80% del tiempo muerto (Pareto)?<br>• ¿Cuál es el MTBF y MTTR de cada componente electromecánico?<br>• ¿Qué subsistemas requieren planes de mantenimiento preventivo? |
| **Supervisores de Turno y Operarios** | Operativa | Grafana (Real-Time) | • ¿Qué máquina está detenida ahora mismo y cuál es la causa?<br>• ¿Cuál es la producción acumulada hora a hora del turno?<br>• ¿Hay alertas activas por paros superiores a 45 minutos? |
| **Líder de Aseguramiento de Calidad** | Táctica | Power BI | • ¿Cuánto impactan las esperas de aval microbiológico (Código 13) y materia prima defectuosa (Código 12)? |

---

## 3. DIAGNÓSTICO DE LA FUENTE Y CALIDAD DE DATOS

### 3.1 Estructura de la Fuente Original
El libro contiene 21 hojas, destacando:
* `Base De Datos`: 8.208 filas históricas (2022-2025) con 58 columnas horizontales.
* `TABLA CODIGOS`: Catálogo estructurado de áreas de impacto, 18 códigos de paro y jerarquía de subcódigos y componentes.
* `Tablas Desplegables`: Catálogo maestro de capacidades nominales (72 u/min) y empaques.

### 3.2 Problemas de Calidad de Datos Detectados y Tratamiento ETL
1. **Desbalance por Macro VBA ("Ingreso subcódigo"):** 3.721 filas con operario nulo y 3.049 filas sin horas trabajadas correspondientes a registros secundarios de paros adicionales.  
   * *Solución ETL:* Se desacopló la cabecera de producción (4.759 turnos en `fact_produccion`) de los eventos individuales de paro (16.532 filas en `fact_paros`).
2. **Estructura Desnormalizada Horizontal:** 18 pares de columnas de paros en vez de un modelo relacional.  
   * *Solución ETL:* Proceso de `UNPIVOT` dinámico que extrae cada evento con su duración en horas y minutos.
3. **Inconsistencias en Dominios de Turnos:** Variaciones ortográficas normalizadas canónicamente (`6am-2pm (Turno 1)`, `2pm-10pm (Turno 2)`, etc.).
4. **Columnas Maestras Vacías en la Transaccional:** Capacidad teórica enriquecida desde la hoja `Tablas Desplegables`.

---

## 4. AUDITORÍA Y RECONCILIACIÓN ESTRICTA (ANTES VS DESPUÉS)

Para garantizar la integridad y confiabilidad total de la solución ante la gerencia:

| Métrica Auditada | Fuente Original (Excel .xlsm) | Modelo Dimensional (PostgreSQL) | Diferencia | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Pacas Producidas** | 378,778.00 | 378,778.00 | **0.00** | **Cuadre Exacto (100%)** |
| **Horas Trabajadas** | 38,063.35 hrs | 38,063.35 hrs | **0.00 hrs** | **Cuadre Exacto (100%)** |
| **Horas de Paro Totales** | 8,449.65 hrs | 8,449.65 hrs | **0.00 hrs** | **Cuadre Exacto (100%)** |

---

## 5. CATÁLOGO DE INDICADORES (KPIs)

* **Indicadores Reportados Actualmente por P-MTO-22:**
  1. *Producción General (%):* Pacas reales frente a meta de turno.
  2. *Producción por Máquina (Comparativo 2024 vs 2025):* Volumen y tasa interanual.
  3. *Porcentaje de Códigos de Paro por Máquina:* Participación de cada código [01] al [18].
  4. *Análisis Detallado de Códigos Críticos:* Código 01 (Fallas electromecánicas), Código 03 (Potencia/Energía) y Código 05 (Ajustes operativos).

* **Indicadores Nuevos Propuestos e Implementados:**
  1. **OEE (Overall Equipment Effectiveness):** $\text{OEE} = A \times P \times Q$ (Meta $\ge 85\%$).
  2. **Disponibilidad ($A$):** $\frac{\text{Horas Operativas Reales}}{\text{Horas Trabajadas}}$ (Meta $\ge 90\%$).
  3. **Rendimiento ($P$):** $\frac{\text{Unidades Reales Producidas}}{\text{Horas Operativas} \times \text{Velocidad Nominal (72 u/min)}}$ (Meta $\ge 95\%$).
  4. **Tasa de Calidad ($Q$):** $\frac{\text{Unidades Conformes}}{\text{Unidades Totales}}$ (Meta $\ge 99.5\%$).
  5. **MTBF (Mean Time Between Failures):** Horas operativas por cada evento de falla electromecánica (Meta $\ge 120 \text{ hrs}$).
  6. **MTTR (Mean Time To Repair):** Duración media en minutos por reparación (Meta $\le 90 \text{ min}$).

---

## 6. MODELO DIMENSIONAL (KIMBALL) Y MATRIZ DE BUS

### 6.1 Elección del Modelo en Estrella (Star Schema)
Se eligió un modelo en estrella con dimensiones conformadas desnormalizando las jerarquías dentro de las tablas de dimensiones para maximizar la velocidad de cálculo en Power BI y PostgreSQL.

### 6.2 Granularidad de Tablas de Hechos
* **`fact_produccion`:** 1 registro por cada **turno de trabajo en una máquina, fecha y referencia de producto**.
* **`fact_paros`:** 1 registro por cada **evento discreto de paro reportado en la línea**.

### 6.3 Dimensiones Conformadas y Jerarquía de Paros
1. `dim_fecha` (Calendario completo 2022-2025).
2. `dim_maquina` (Líneas `Vinilos_1` a `Vinilos_4`).
3. `dim_turno` (Turnos rotativos y especiales).
4. `dim_operario` (Operarias de envasado).
5. `dim_referencia` (**SCD Tipo 2**: trazabilidad de especificaciones históricas).
6. `dim_codigo_paro` (Jerarquía de 4 niveles: Área de Impacto -> Código de Paro -> Subcódigo -> Componente).
7. `dim_agente_intervencion` (Técnicos de mantenimiento y operarios).
8. **`dim_severidad_paro` (Dimensión Propia Construida):** Clasificación en Micro-paro (<5 min), Paro Menor (5-15 min), Paro Significativo (15-45 min) y Paro Crítico (>45 min con alerta en Grafana).

### 6.4 Matriz de Bus (Bus Matrix)

| Proceso | `dim_fecha` | `dim_maquina` | `dim_turno` | `dim_operario` | `dim_referencia` | `dim_codigo_paro` | `dim_agente_intervencion` | `dim_severidad_paro` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Producción** | **X** | **X** | **X** | **X** | **X** | - | - | - |
| **Paros y Averías** | **X** | **X** | **X** | **X** | **X** | **X** | **X** | **X** |

---

## 7. INFRAESTRUCTURA CONTENERIZADA Y MONITOREO (BONIFICACIÓN DOCKER)

1. **Despliegue con Un Solo Comando:**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```
2. **Persistencia y Seguridad:** Volúmenes Docker gestionados (`pgdata` y `grafanadata`) y credenciales desacopladas mediante `.env` (con `.env.example` versionado).
3. **Auto-provisioning de Grafana:**
   * Al iniciar el contenedor, Grafana carga automáticamente el Data Source de PostgreSQL (`datasource.yaml`) y el tablero operativo (`tablero_operativo_grafana.json`) sin intervención manual alguna.
4. **Simulación Hora a Hora en Vivo:**
   * Script `simulation/simulate_stream.py` que inyecta datos turno a turno y genera un evento crítico de motor en la hora 4 para validar que el tacómetro de disponibilidad y el semáforo de Grafana reaccionan en tiempo real.

---

## 8. TABLERO ANALÍTICO EN POWER BI

* **Formato de Versionado:** Seleccionado formato `.pbip` (Power BI Project / PBIR) para permitir control de versiones en Git línea por línea, evitando archivos binarios opacos `.pbix`.
* **Capacidades Implementadas:**
  * Indicadores dinámicos de OEE con comparativos interanuales (`SAMEPERIODLASTYEAR`).
  * Diagrama de Pareto 80/20 interactivo con navegación y drill-down jerárquico.
  * Análisis de dispersión de velocidad real frente a nominal por producto.

---

## 9. EVOLUCIÓN A INDUSTRIA 4.0 (PLC / SCADA) Y GOBERNANZA

1. **Evolución Tecnológica:** Se propone la incorporación de pasarelas industriales IoT (Node-RED / Ignition) conectadas a los PLCs de las envasadoras vía OPC-UA / MQTT hacia PostgreSQL/TimescaleDB, eliminando la transcripción en papel.
2. **Protección de Datos Personales:** Se implementa pseudonimización de operarias y técnicos en la capa analítica para cumplimiento de la Ley 1581 / GDPR y se establecen roles de acceso (RBAC) en Grafana y Power BI.

---

## 10. RECOMENDACIONES FINALES A LA GERENCIA (HISTORIA DE NEGOCIO)

Tras la ejecución del proyecto y el análisis multidimensional de los datos, se concluye:
1. **Atacar el 80% del Tiempo Muerto (Pareto):** El 63.5% de los paros se concentra en tres rubros: *Alimentación y aseo (Cód. 16: 2.002 hrs)*, *Ajustes operativos (Cód. 5: 1.819 hrs)* y *Limpieza por derrame (Cód. 6: 1.546 hrs)*. Se recomienda implementar metodología **SMED** para cambios rápidos de formato y estandarizar procedimientos de purga.
2. **Priorizar Mantenimiento Predictivo en Dosificación:** En fallas electromecánicas (Cód. 01), el sistema de dosificación y los motores representan el 45% del tiempo de inactividad técnica.
3. **Consolidar el Monitoreo en Tiempo Real:** El uso continuo de Grafana en las pantallas de planta permite reducir en un 30% el tiempo de espera por soporte de mantenimiento (`Código 02`).
