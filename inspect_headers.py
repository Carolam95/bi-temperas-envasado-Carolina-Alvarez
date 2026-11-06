import pandas as pd

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

df_raw = pd.read_excel(EXCEL_PATH, sheet_name="Base De Datos", header=None, nrows=10)
print("=== Base De Datos: First 6 rows ===")
for idx, row in df_raw.iloc[:6].iterrows():
    vals = [str(x) if pd.notna(x) else "" for x in row.values]
    non_empty = [(i, v) for i, v in enumerate(vals) if v != ""]
    print(f"Row {idx}: {len(non_empty)} non-empty cells -> {non_empty[:15]}")

df_sub_raw = pd.read_excel(EXCEL_PATH, sheet_name="Base de datos de Sub codigos", header=None, nrows=10)
print("\n=== Base de datos de Sub codigos: First 6 rows ===")
for idx, row in df_sub_raw.iloc[:6].iterrows():
    vals = [str(x) if pd.notna(x) else "" for x in row.values]
    non_empty = [(i, v) for i, v in enumerate(vals) if v != ""]
    print(f"Row {idx}: {len(non_empty)} non-empty cells -> {non_empty[:15]}")
