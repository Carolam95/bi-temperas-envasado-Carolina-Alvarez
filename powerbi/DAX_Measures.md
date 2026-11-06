# Catálogo de Medidas DAX y Formato de Versionado Power BI
**Proyecto de Inteligencia de Negocios: Líneas de Envasado**

---

## 1. Justificación del Formato de Versionado: `.pbip` (Power BI Project)

Para cumplir con el requerimiento de versionado en Git sin binarios opacos, se seleccionó el formato **`.pbip` (Power BI Project / PBIR)**:

* **¿Por qué NO el archivo tradicional `.pbix`?**
  * El formato `.pbix` es un archivo binario empaquetado (ZIP propietario). Cuando dos personas editan el mismo archivo, Git no puede comparar líneas (`diff`) ni resolver conflictos de merge, obligando a descartar el trabajo de uno de los colaboradores. Además, almacena contraseñas y datos en caché dentro del archivo.
* **Ventajas del formato `.pbip`:**
  1. **Trazabilidad y Git Diff Legible:** Desglosa el proyecto en carpetas con archivos de texto plano legibles:
     * `*.Report/definition.pbir`: Estructura visual de los tableros.
     * `*.Dataset/model.bim` o definición TMDL (Tabular Model Definition Language): Define tablas, relaciones, jerarquías y medidas DAX en texto claro.
  2. **Colaboración Real en Equipo:** Ambos integrantes pueden trabajar simultáneamente: uno en las medidas DAX del modelo y otro en el diseño de los reportes visuales, realizando `git commit` y `git merge` limpios.
  3. **Seguridad y Parámetros:** Permite parametrizar las cadenas de conexión a PostgreSQL sin exponer contraseñas en el repositorio.

---

## 2. Catálogo de Medidas DAX (Data Analysis Expressions)

### 2.1 Medidas Base (Volúmenes y Tiempos)
```dax
// Total de pacas producidas
Total Pacas = 
SUM(fact_produccion[pacas_producidas])

// Total de horas trabajadas reportadas en turnos
Total Horas Trabajadas = 
SUM(fact_produccion[horas_trabajadas])

// Total de horas de paro reportadas en eventos atómicos
Total Horas Paro = 
SUM(fact_paros[duracion_horas])

// Horas netas de operación de las máquinas
Horas Operativas = 
[Total Horas Trabajadas] - [Total Horas Paro]

// Unidades reales de envases producidos
Unidades Reales = 
SUM(fact_produccion[unidades_reales])

// Capacidad nominal ideal teórica según estándar de referencia
Unidades Ideales = 
SUM(fact_produccion[unidades_ideales])
```

### 2.2 Componentes del OEE (Overall Equipment Effectiveness)
```dax
// Disponibilidad (A) = Horas Operativas / Horas Programadas
Disponibilidad % = 
DIVIDE([Horas Operativas], [Total Horas Trabajadas], 0)

// Rendimiento (P) = Unidades Reales / Unidades Ideales a Velocidad Nominal
Rendimiento % = 
DIVIDE([Unidades Reales], [Unidades Ideales], 0)

// Calidad (Q) = Tasa de unidades conformes
Calidad % = 
AVERAGE(fact_produccion[calidad_pct]) / 100.0

// OEE Global = A * P * Q
OEE % = 
[Disponibilidad %] * [Rendimiento %] * [Calidad %]
```

### 2.3 Medidas de Inteligencia de Tiempo (Time Intelligence)
```dax
// Producción en el mismo periodo del año anterior
Pacas SPLY = 
CALCULATE(
    [Total Pacas],
    SAMEPERIODLASTYEAR(dim_fecha[fecha])
)

// Variación interanual porcentual de pacas
Variacion YoY Pacas % = 
DIVIDE([Total Pacas] - [Pacas SPLY], [Pacas SPLY], 0)

// OEE del mismo periodo del año anterior
OEE SPLY % = 
CALCULATE(
    [OEE %],
    SAMEPERIODLASTYEAR(dim_fecha[fecha])
)

// Variación de puntos porcentuales en OEE
Delta OEE YoY Puntos = 
[OEE %] - [OEE SPLY %]

// Producción acumulada mes a la fecha (MTD)
Produccion MTD = 
TOTALMTD([Total Pacas], dim_fecha[fecha])

// Producción acumulada año a la fecha (YTD)
Produccion YTD = 
TOTALYTD([Total Pacas], dim_fecha[fecha])
```

### 2.4 Medidas de Mantenimiento y Confiabilidad
```dax
// Cantidad de averías electromecánicas registradas (Código 01)
Conteo Fallas Codigo 01 = 
CALCULATE(
    COUNTROWS(fact_paros),
    dim_codigo_paro[codigo_numero] = 1
)

// MTBF (Mean Time Between Failures) en horas
MTBF Horas = 
DIVIDE([Horas Operativas], [Conteo Fallas Codigo 01], BLANK())

// MTTR (Mean Time To Repair) en minutos promedio
MTTR Minutos = 
CALCULATE(
    AVERAGE(fact_paros[duracion_minutos]),
    dim_codigo_paro[codigo_numero] = 1
)
```

### 2.5 Análisis de Pareto Acumulado de Paros
```dax
// Porcentaje acumulado de horas de paro (Curva 80/20 de Pareto)
Pareto Paro % Acumulado = 
VAR TotalParoGeneral = CALCULATE([Total Horas Paro], ALLSELECTED(dim_codigo_paro))
VAR HorasActuales = [Total Horas Paro]
VAR HorasMayores = 
    CALCULATE(
        [Total Horas Paro],
        FILTER(
            ALLSELECTED(dim_codigo_paro),
            [Total Horas Paro] >= HorasActuales
        )
    )
RETURN
DIVIDE(HorasMayores, TotalParoGeneral, 0)
```

---

## 3. Estructura de Páginas y Navegación del Tablero Power BI

1. **Página 1: Resumen Gerencial y OEE (Estratégico):**
   * Tarjetas KPI de OEE, Disponibilidad, Rendimiento y Calidad frente al año anterior.
   * Gráfico de líneas interanual: Comparativo 2024 vs 2025 de producción general por máquina.
   * Filtros por Máquina, Año, Trimestre y Línea de Producto.
2. **Página 2: Análisis Detallado de Paros y Confiabilidad (Táctico):**
   * Gráfico de Pareto (Barras por código de paro y línea acumulada al 80%).
   * Drill-down jerárquico interactivo: Área de Impacto -> Código de Paro -> Subcódigo -> Componente.
   * Matriz de MTBF y MTTR por subsistema de máquina.
3. **Página 3: Rendimiento Operativo por Turno y Referencia (Operativo):**
   * Dispersión de velocidad real vs velocidad nominal por referencia.
   * Eficiencia por turno y cuadrilla operaria.
