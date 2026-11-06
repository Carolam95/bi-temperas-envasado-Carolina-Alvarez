import pandas as pd

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

print("=== Sheet: Tiempos ===")
df_t = pd.read_excel(EXCEL_PATH, sheet_name="Tiempos")
for col in df_t.columns:
    s = df_t[col].dropna()
    if len(s) > 0:
        print(f"Col '{col}': {s.values[:8]}")

print("\n=== Sheet: Tablas Desplegables ===")
df_d = pd.read_excel(EXCEL_PATH, sheet_name="Tablas Desplegables")
for col in df_d.columns:
    s = df_d[col].dropna()
    if len(s) > 0:
        print(f"Col '{col}': {s.values[:5]}")
