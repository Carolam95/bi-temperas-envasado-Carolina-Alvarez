import openpyxl
import pandas as pd
import json
import os

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

def inspect():
    print(f"Loading workbook: {EXCEL_PATH}...")
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=False, keep_vba=True)
    sheet_names = wb.sheetnames
    print(f"Sheets found ({len(sheet_names)}): {sheet_names}")
    
    summary = {}
    for name in sheet_names:
        ws = wb[name]
        max_row = ws.max_row
        max_col = ws.max_column
        
        # sample first 3 rows
        sample_rows = []
        for r in range(1, min(max_row + 1, 5)):
            row_vals = [ws.cell(r, c).value for c in range(1, min(max_col + 1, 30))]
            if any(v is not None for v in row_vals):
                sample_rows.append([str(v) if v is not None else "" for v in row_vals])
                
        summary[name] = {
            "max_row": max_row,
            "max_col": max_col,
            "sample_rows": sample_rows
        }
        print(f"\n--- Sheet: {name} (Rows: {max_row}, Cols: {max_col}) ---")
        for i, row in enumerate(sample_rows[:3]):
            print(f" Row {i+1}: {row[:10]}")

    with open("excel_inspection.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("\nInspection saved to excel_inspection.json")

if __name__ == "__main__":
    inspect()
