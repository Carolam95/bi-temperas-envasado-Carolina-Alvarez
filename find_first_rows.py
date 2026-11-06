import openpyxl

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)

for sname in ["Base De Datos", "Base de datos de Sub codigos"]:
    ws = wb[sname]
    print(f"\n=== Scanning {sname} for first non-empty rows ===")
    found = 0
    for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        non_empty = [(c_idx, val) for c_idx, val in enumerate(row, start=1) if val is not None and str(val).strip() != ""]
        if non_empty:
            print(f"Row {r_idx}: {len(non_empty)} cells -> {non_empty[:12]}")
            found += 1
            if found >= 5:
                break
