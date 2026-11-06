import openpyxl
import json

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)

ws_base = wb["Base De Datos"]
base_headers = [cell for cell in next(ws_base.iter_rows(min_row=9, max_row=9, values_only=True))]
print("=== Base De Datos Headers (58 columns) ===")
for i, h in enumerate(base_headers, 1):
    clean_h = str(h).replace('\n', ' ') if h is not None else f"EMPTY_{i}"
    print(f"Col {i}: {clean_h}")

ws_sub = wb["Base de datos de Sub codigos"]
sub_headers = [cell for cell in next(ws_sub.iter_rows(min_row=8, max_row=8, values_only=True))]
print("\n=== Base de datos de Sub codigos Headers (19 columns) ===")
for i, h in enumerate(sub_headers, 1):
    clean_h = str(h).replace('\n', ' ') if h is not None else f"EMPTY_{i}"
    print(f"Col {i}: {clean_h}")

# Also inspect TABLA CODIGOS content completely
ws_codes = wb["TABLA CODIGOS"]
print("\n=== TABLA CODIGOS rows ===")
for r_idx, row in enumerate(ws_codes.iter_rows(values_only=True), start=1):
    non_empty = [(c_idx, str(val).strip()) for c_idx, val in enumerate(row, start=1) if val is not None and str(val).strip() != ""]
    if non_empty:
        print(f"R{r_idx}: {non_empty}")
