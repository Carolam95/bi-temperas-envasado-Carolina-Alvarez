import pandas as pd
import json

EXCEL_PATH = r"C:\Users\USUARIO\Downloads\SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm"

def inspect_details():
    # 1. Base De Datos
    print("Reading 'Base De Datos'...")
    df_base = pd.read_excel(EXCEL_PATH, sheet_name="Base De Datos", nrows=10)
    print("Base De Datos columns (total %d):" % len(df_base.columns))
    for i, col in enumerate(df_base.columns):
        print(f"  {i}: {col}")

    # 2. Base de datos de Sub codigos
    print("\nReading 'Base de datos de Sub codigos'...")
    df_sub = pd.read_excel(EXCEL_PATH, sheet_name="Base de datos de Sub codigos", nrows=10)
    print("Base de datos de Sub codigos columns (total %d):" % len(df_sub.columns))
    for i, col in enumerate(df_sub.columns):
        print(f"  {i}: {col}")

    # 3. TABLA CODIGOS
    print("\nReading 'TABLA CODIGOS'...")
    df_cod = pd.read_excel(EXCEL_PATH, sheet_name="TABLA CODIGOS", header=None).dropna(how='all')
    print("TABLA CODIGOS shape:", df_cod.shape)
    print(df_cod.head(15))

    # 4. Tiempos
    print("\nReading 'Tiempos'...")
    df_tiempos = pd.read_excel(EXCEL_PATH, sheet_name="Tiempos")
    print("Tiempos shape:", df_tiempos.shape)
    print(df_tiempos.head(10))

if __name__ == "__main__":
    inspect_details()
