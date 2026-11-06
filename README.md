# Solución de Inteligencia de Negocios End-to-End: Líneas de Envasado de Vinilos y Témperas

[![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Grafana](https://img.shields.io/badge/Grafana-10.4-orange.svg)](https://grafana.com/)
[![Power BI](https://img.shields.io/badge/Power_BI-PBIP-F2C811.svg)](https://powerbi.microsoft.com/)

Solución integral de Inteligencia de Negocios de extremo a extremo que moderniza el registro histórico de producción y paros (procedimiento `P-MTO-22`), pasando de un esquema manual en hojas de cálculo con macros a un **modelo dimensional relacional en estrella (Kimball)**, con **despliegue contenerizado en Docker**, **monitoreo en tiempo real con alertas en Grafana** y **tableros analíticos estratégicos con cálculo de OEE en Power BI**.

---

## 🏗 Arquitectura de la Solución

```
+------------------------------------+
|  Fuente: Excel (.xlsm)             |
|  - Base De Datos (8.208 filas)     |
|  - TABLA CODIGOS (Jerarquía Paros) |
|  - Tablas Desplegables             |
+-----------------+------------------+
                  |
                  v
+------------------------------------+
|  Proceso ETL (Python + Pandas)     |
|  - Desacople Producción vs Paros   |
|  - Unpivot de 18 columnas de paro  |
|  - SCD Tipo 2 en Referencias       |
|  - Reconciliación 100% Exacta      |
+-----------------+------------------+
                  |
                  v
+------------------------------------+
|  PostgreSQL 15 (Docker)            |
|  - fact_produccion (4.759 turnos)  |
|  - fact_paros (16.532 eventos)     |
|  - 8 Dimensiones Conformadas       |
+-----------------+------------------+
         |                 |
         v                 v
+------------------+  +-------------------+
| Grafana (Docker) |  | Power BI (.pbip)  |
| - Near Real-Time |  | - OEE Dinámico    |
| - Alertas Vivas  |  | - Pareto 80/20    |
| - Auto-Provision |  | - Inteligencia YoY|
+------------------+  +-------------------+
```

---

## 🚀 Despliegue y Reproducción en un Solo Comando

### 1. Requisitos Previos
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución.
* Python 3.10 o superior.
* DBeaver o cliente SQL compatible con PostgreSQL.
* Power BI Desktop (opcional para consumo de reportes).

### 2. Configurar Variables de Entorno
```bash
cd docker
copy .env.example .env
```

### 3. Levantar Infraestructura Contenerizada
```bash
docker-compose up -d
```
*Este comando levanta automáticamente:*
* **PostgreSQL 15** en el puerto `5432` con la base de datos `bi_temperas` y el script DDL precargado.
* **Grafana 10.4** en el puerto `3000` con el **Data Source** y el **Dashboard Operativo ya aprovisionados automáticamente** (sin configuración manual).

### 4. Ejecutar el Proceso ETL
```bash
# Crear entorno virtual e instalar librerías
python -m venv .venv
# En Windows:
.venv\Scripts\activate
pip install -r requirements.txt

# Ejecutar el pipeline ETL
python etl/pipeline.py
```
*El script procesa la fuente, aplica reglas de calidad, reconcilia las cifras al 100% y carga tanto en PostgreSQL como en archivos CSV/SQLite.*

### 5. Acceder a los Tableros y Monitoreo en Vivo
* **Grafana:** Ingresar en el navegador a `http://localhost:3000`  
  * *Usuario:* `admin` | *Contraseña:* `admin`
  * Abrir la carpeta **Líneas de Envasado** -> **Tablero de Monitoreo Near Real-Time**.
* **Simulación Hora a Hora en Tiempo Real:**
  ```bash
  python simulation/simulate_stream.py
  ```
  *Observa en Grafana cómo los tacómetros de disponibilidad y el semáforo reaccionan en vivo y disparan alertas rojas ante paros mayores a 45 minutos.*
* **DBeaver:** Conectar a `localhost:5432`, base de datos `bi_temperas`, esquema `bi_temperas` y ejecutar las consultas de `sql/02_consultas_analiticas.sql`.

---

## 📊 Conciliación y Auditoría de Datos (100% Exacto)

| Métrica | Fuente Original (.xlsm) | Modelo Final Cargado | Diferencia | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Pacas Producidas** | 378,778.00 | 378,778.00 | **0.00** | **Cuadre Exacto** |
| **Horas Trabajadas** | 38,063.35 hrs | 38,063.35 hrs | **0.00 hrs** | **Cuadre Exacto** |
| **Horas de Paro Totales**| 8,449.65 hrs | 8,449.65 hrs | **0.00 hrs** | **Cuadre Exacto** |

---

## 📁 Estructura del Repositorio

```
proyecto-bi-temperas/
├── docker/
│   ├── docker-compose.yml          # Despliegue de PostgreSQL y Grafana
│   ├── .env.example                # Plantilla de variables de entorno seguras
│   └── grafana/provisioning/
│       ├── datasources/datasource.yaml  # Conexión automática a PostgreSQL
│       └── dashboards/
│           ├── dashboard_provider.yaml  # Proveedor de tableros
│           └── tablero_operativo_grafana.json # Dashboard operacional completo
├── sql/
│   ├── 01_ddl_postgresql.sql      # DDL del modelo dimensional en estrella
│   └── 02_consultas_analiticas.sql # Consultas avanzadas con window functions
├── etl/
│   └── pipeline.py                 # Pipeline reproducible de extracción, limpieza y carga
├── simulation/
│   └── simulate_stream.py          # Simulador hora a hora para pruebas en vivo
├── docs/
│   ├── 01_diagnostico_y_calidad.md # Diagnóstico técnico y auditoría de datos
│   ├── 02_catalogo_indicadores.md  # Catálogo de KPIs (OEE, MTBF, MTTR, etc.)
│   ├── 03_modelo_dimensional_kimball.md # Grano, Bus Matrix y SCD Tipo 2
│   ├── 04_arquitectura_gobernanza_futuro.md # Comparativa, SCADA y Ley 1581
│   └── BI_ProyectoFinal_Apellido1_Apellido2.md # Informe técnico formal para entrega
├── powerbi/
│   └── DAX_Measures.md             # Justificación formato .pbip y medidas DAX
├── requirements.txt                # Dependencias de Python
└── README.md                       # Documentación principal del proyecto
```
