import pandas as pd

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

df_base = pd.read_excel(EXCEL_PATH, sheet_name="Base De Datos", skiprows=8)
df_base.columns = [str(c).replace('\n', ' ').strip() for c in df_base.columns]

# Filter rows where Operario is null
null_op = df_base[df_base['Operario'].isna()]
print("Sample rows where Operario is null:")
print(null_op[['Fecha', 'Maquina', 'Operario', 'Referencia', 'Horas trabajadas', 'Pacas producidas', 'Tiempo de Paro', 'Tipo de paro']].head(10))

# Filter rows where Horas trabajadas > 0
with_prod = df_base[df_base['Horas trabajadas'] > 0]
print("\nSample rows where Horas trabajadas > 0:")
print(with_prod[['Fecha', 'Maquina', 'Operario', 'Referencia', 'Horas trabajadas', 'Pacas producidas', 'Tiempo de Paro']].head(5))

# Check if there are rows with both Horas trabajadas > 0 AND Tiempo de Paro > 0
both = df_base[(df_base['Horas trabajadas'] > 0) & (df_base['Tiempo de Paro'] > 0)]
print(f"\nRows with BOTH Horas trabajadas > 0 and Tiempo de Paro > 0: {len(both)}")
print(both[['Fecha', 'Maquina', 'Operario', 'Referencia', 'Horas trabajadas', 'Pacas producidas', 'Tiempo de Paro']].head(5))

# Check rows with Horas trabajadas is NA but Tiempo de Paro > 0
only_stop = df_base[(df_base['Horas trabajadas'].isna()) & (df_base['Tiempo de Paro'] > 0)]
print(f"\nRows with Horas trabajadas is NA and Tiempo de Paro > 0: {len(only_stop)}")
print(only_stop[['Fecha', 'Maquina', 'Operario', 'Referencia', 'Tiempo de Paro', 'Tipo de paro', 'Codigo de paro 1', 'Codigo 1 en horas']].head(5))

# Check how VBA macro works: inspect VBA module if possible
