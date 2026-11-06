import pandas as pd

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

df_base = pd.read_excel(EXCEL_PATH, sheet_name="Base De Datos", skiprows=8)
df_base.columns = [str(c).replace('\n', ' ').strip() for c in df_base.columns]

for idx in range(15):
    row = df_base.iloc[idx]
    non_nulls = {k: v for k, v in row.items() if pd.notna(v) and str(v) != '0' and str(v) != '0.0' and str(v) != ''}
    print(f"Row {idx} (Excel row {idx+10}): {non_nulls}")
