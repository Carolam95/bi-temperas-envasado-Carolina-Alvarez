import openpyxl
import pandas as pd
import numpy as np

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

df_base = pd.read_excel(EXCEL_PATH, sheet_name="Base De Datos", skiprows=8)

# Normalize column names: replace non-ascii chars, newlines, multiple spaces
def clean_col(name):
    c = str(name).replace('\n', ' ').strip()
    c = c.replace('Ao', 'Anio').replace('Año', 'Anio').replace('Á', 'A').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
    return c

df_base.columns = [clean_col(c) for c in df_base.columns]
print(f"Shape of Base De Datos: {df_base.shape}")

print("\nDate range:")
print("Min fecha:", df_base['Fecha'].min(), "Max fecha:", df_base['Fecha'].max())
print("Unique Anios:", df_base['Anio'].dropna().unique())
print("Unique Maquinas:", df_base['Maquina'].dropna().unique())
print("Unique Turnos:", df_base['Turno'].dropna().unique())

print("\n--- Summary of key measures in raw Base De Datos ---")
print("Sum Pacas producidas:", df_base['Pacas producidas'].sum(skipna=True))
print("Sum Horas trabajadas:", df_base['Horas trabajadas'].sum(skipna=True))
print("Sum Tiempo de Paro:", df_base['Tiempo de Paro'].sum(skipna=True))

stop_cols = [c for c in df_base.columns if 'en horas' in c.lower() or 'a horas' in c.lower()]
print("\nIndividual stop columns sum:")
sum_stops = 0
for col in stop_cols:
    val = pd.to_numeric(df_base[col], errors='coerce').sum()
    sum_stops += val
    print(f"  {col}: {val:.2f} hrs")
print(f"Total across all stop columns: {sum_stops:.2f} hrs")

print("\n--- Data Quality findings in Base De Datos ---")
print("Total rows:", len(df_base))
print("Rows with null Operario:", df_base['Operario'].isna().sum())
print("Rows with null Referencia:", df_base['Referencia'].isna().sum())
print("Rows with null Turno:", df_base['Turno'].isna().sum())
print("Rows with null Horas trabajadas:", df_base['Horas trabajadas'].isna().sum())
print("Rows with null Pacas producidas:", df_base['Pacas producidas'].isna().sum())
print("Rows with Horas trabajadas == 0:", (df_base['Horas trabajadas'] == 0).sum())
print("Rows with Pacas producidas == 0:", (df_base['Pacas producidas'] == 0).sum())

# Check Sub codigos sheet
df_sub = pd.read_excel(EXCEL_PATH, sheet_name="Base de datos de Sub codigos", skiprows=7)
df_sub.columns = [clean_col(c) for c in df_sub.columns]
print(f"\nShape of Base de datos de Sub codigos: {df_sub.shape}")
print("Subcodigos min fecha:", df_sub['Fecha'].min(), "max fecha:", df_sub['Fecha'].max())
print("Subcodigos unique Anios:", df_sub['Anio'].dropna().unique())
print("Subcodigos Pacas producidas sum:", df_sub['Pacas producidas'].sum(skipna=True))
sub_stop_cols = [c for c in df_sub.columns if 'a horas' in c.lower() or 'en horas' in c.lower()]
for col in sub_stop_cols:
    val = pd.to_numeric(df_sub[col], errors='coerce').sum()
    print(f"  Sub sheet {col}: {val:.2f} hrs")

# Check Tiempos (Master speed table)
df_tiempos = pd.read_excel(EXCEL_PATH, sheet_name="Tiempos")
print("\nTiempos sheet columns:", df_tiempos.columns[:10])
print(df_tiempos.iloc[:15, :10])
