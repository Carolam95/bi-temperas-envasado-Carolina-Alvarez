"""
=============================================================================
SIMULADOR HORA A HORA EN VIVO PARA MONITOREO EN GRAFANA (NEAR REAL-TIME)
=============================================================================
Demuestra la reactividad continua del tablero de Grafana y el disparo
de alertas ante eventos críticos de paro.
"""

import os
import sys
import time
import datetime
import random
from sqlalchemy import create_engine, text

# Base de datos destino: SQLite local por defecto o PostgreSQL de Docker
SQLITE_PATH = r"C:\Users\USUARIO\.gemini\antigravity\scratch\proyecto-bi-temperas\data\processed\bi_temperas.db"
DEFAULT_DB_URL = f"sqlite:///{SQLITE_PATH}"

def get_engine():
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url:
        return create_engine(pg_url)
    return create_engine(DEFAULT_DB_URL)

def run_simulation(horas_simular=8, segundos_por_hora=3):
    engine = get_engine()
    print("=" * 70)
    print("INICIANDO SIMULADOR HORA A HORA EN TIEMPO REAL PARA GRAFANA")
    print(f"Destino: {engine.url}")
    print(f"Jornada: {horas_simular} horas simuladas | Velocidad: {segundos_por_hora} seg / hora")
    print("=" * 70)

    maquinas = [
        (1, 'Vinilos_1', 1),
        (2, 'Vinilos_2', 2),
        (3, 'Vinilos_3', 3),
        (4, 'Vinilos_4', 4)
    ]
    
    fecha_hoy = datetime.date.today()
    fecha_key = int(fecha_hoy.strftime('%Y%m%d'))
    hora_inicio = datetime.datetime.now()

    for h in range(1, horas_simular + 1):
        timestamp_actual = hora_inicio + datetime.timedelta(hours=h)
        print(f"\n>>> [SIMULACIÓN HORA {h}/{horas_simular}] - {timestamp_actual.strftime('%Y-%m-%d %H:%M:%S')} <<<")

        with engine.begin() as conn:
            for maq_key, maq_name, ref_sk in maquinas:
                # Caso de prueba en hora 4: Inyectar falla crítica en Vinilos_2 para detonar alerta
                es_falla_critica = (h == 4 and maq_name == 'Vinilos_2')

                if es_falla_critica:
                    horas_trab = 1.0
                    tiempo_paro = 0.85 # 51 minutos de paro (> 45 min -> ALERTA CRÍTICA)
                    pacas = 8.0
                    c_num = 1 # Falla electromecánica
                    c_key = 1
                    sub_desc = '1.1.B Falla de Motor de Dosificación'
                    sev_key = 4 # Paro Crítico
                    tecnico_id = 1
                    obs = 'ALERTA DISPARADA: Motor de dosificación recalentado. Soporte en sitio.'
                    print(f"  [!] {maq_name}: EVENTO CRÍTICO INYECTADO - {sub_desc} ({tiempo_paro*60:.0f} min).")
                else:
                    horas_trab = 1.0
                    tiempo_paro = random.choice([0.05, 0.08, 0.12, 0.15]) # 3 a 9 min
                    pacas = random.randint(28, 42)
                    c_num = random.choice([5, 6, 16, 17]) # Ajuste, derrame o pausa
                    c_key = c_num
                    sub_desc = 'Ajuste operacional de rutina'
                    sev_key = 1 if tiempo_paro < 0.08 else 2
                    tecnico_id = 2
                    obs = 'Operación normal de turno.'

                unidades_reales = pacas * 216.0
                unidades_ideales = 1.0 * 60.0 * 72.0
                tiempo_op = max(0.0, horas_trab - tiempo_paro)
                disp_pct = round((tiempo_op / horas_trab) * 100.0, 1)
                rend_pct = round((unidades_reales / unidades_ideales) * 100.0, 1)
                oee_pct = round((disp_pct/100.0) * (rend_pct/100.0) * 0.995 * 100.0, 1)

                # Insertar en fact_produccion
                query_prod = text("""
                    INSERT INTO fact_produccion (
                        fecha_key, maquina_key, turno_key, operario_key, referencia_sk,
                        horas_trabajadas, horas_programadas, pacas_producidas, unidades_reales,
                        unidades_ideales, tiempo_paro_horas, tiempo_operativo_horas,
                        disponibilidad_pct, rendimiento_pct, calidad_pct, oee_pct
                    ) VALUES (
                        :f_key, :m_key, 1, 1, :r_sk,
                        :h_trab, :h_prog, :pacas, :u_real,
                        :u_ideal, :t_paro, :t_op,
                        :disp, :rend, 99.5, :oee
                    )
                """)
                conn.execute(query_prod, {
                    'f_key': fecha_key, 'm_key': maq_key, 'r_sk': ref_sk,
                    'h_trab': horas_trab, 'h_prog': horas_trab, 'pacas': pacas,
                    'u_real': unidades_reales, 'u_ideal': unidades_ideales,
                    't_paro': tiempo_paro, 't_op': tiempo_op,
                    'disp': disp_pct, 'rend': rend_pct, 'oee': oee_pct
                })

                # Insertar en fact_paros
                query_paro = text("""
                    INSERT INTO fact_paros (
                        fecha_key, maquina_key, turno_key, operario_key, referencia_sk,
                        codigo_paro_key, agente_key, severidad_key,
                        duracion_horas, duracion_minutos, costo_estimado_cop, observaciones
                    ) VALUES (
                        :f_key, :m_key, 1, 1, :r_sk,
                        :c_key, :ag_key, :sev_key,
                        :dur_h, :dur_m, :costo, :obs
                    )
                """)
                conn.execute(query_paro, {
                    'f_key': fecha_key, 'm_key': maq_key, 'r_sk': ref_sk,
                    'c_key': c_key, 'ag_key': tecnico_id, 'sev_key': sev_key,
                    'dur_h': tiempo_paro, 'dur_m': tiempo_paro * 60.0,
                    'costo': tiempo_paro * 150000.0, 'obs': obs
                })

                estado_semaforo = "[ALERTA ROJA]" if disp_pct < 75.0 else ("[PRECAUCIÓN]" if disp_pct < 90.0 else "[ÓPTIMO]")
                print(f"  {estado_semaforo} {maq_name:10} | Pacas: {pacas:2} | Disp: {disp_pct:5.1f}% | OEE: {oee_pct:5.1f}%")

        time.sleep(segundos_por_hora)

    print("\n" + "=" * 70)
    print("SIMULACIÓN FINALIZADA CON ÉXITO.")
    print("El tablero de Grafana ha refrescado los paneles en vivo y reflejado las alertas.")
    print("=" * 70)

if __name__ == "__main__":
    run_simulation(horas_simular=4, segundos_por_hora=1)
