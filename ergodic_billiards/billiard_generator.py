import os
import time
import glob
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО КОНВЕЙЕРА
# =====================================================================
SEQ_LENGTH = 100            # Длина ряда (количество ударов)
ROWS_PER_TABLE = 35         # Количество орбит на каждый стол
OUTPUT_FILE = "ergodic_billiards_light_dataset.csv"

TABLE_TYPES = ["Bunimovich_Stadium", "Sinai_Billiard", "Elliptic_Focus", "Ergodic_Triangle"]

def safe_num(val, ndigits=4):
    """Защита от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР ХАОТИЧЕСКИХ ОТСКОКОВ
# =====================================================================
def generate_billiard_trajectory(table_type, length, row_idx):
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 23)
    x, y = 0.0, 0.0
    angle = np.random.uniform(0.1, 2 * np.pi - 0.1)
    vx, vy = np.cos(angle), np.sin(angle)
    
    time_series = []
    L, R = 2.0, 1.0
    
    for _ in range(length):
        dt = np.random.uniform(0.5, 2.5)
        x += vx * dt
        y += vy * dt
        
        # Симуляция упрощенных физических отражений от бортов разной формы
        if table_type == "Bunimovich_Stadium":
            if abs(x) > L/2: vx = -vx + np.random.normal(0, 0.01); x = np.sign(x) * (L/2 + R * 0.9)
            if abs(y) > R: vy = -vy + np.random.normal(0, 0.01); y = np.sign(y) * (R * 0.9)
        elif table_type == "Sinai_Billiard":
            if np.sqrt((x-L/2)**2 + (y-L/2)**2) < R * 0.4: vx, vy = -vx, -vy; x, y = x*1.1, y*1.1
            if abs(x) > L or abs(y) > L: vx, vy = -vx, -vy; x, y = np.clip(x, -L, L), np.clip(y, -L, L)
        elif table_type == "Elliptic_Focus":
            if (x**2 / 4.0) + (y**2 / 1.0) > 1.0: vx, vy = -vx + np.random.normal(0, 0.01), -vy; x, y = x*0.9, y*0.9
        else: # Ergodic_Triangle
            if x < 0 or x > L or y < 0 or y > (L - x): vx, vy = -vx, -vy; x, y = np.clip(x, 0.1, L-0.1), np.clip(y, 0.1, L-0.1)

        v_norm = np.sqrt(vx**2 + vy**2) + 1e-12
        vx, vy = vx / v_norm, vy / v_norm
        time_series.append(abs(vx * dt - vy * dt))
        
    return np.array(time_series, dtype=float)

# =====================================================================
# ШАГ 2: АНАЛИЗАТОР (РОВНО 7 НЕУБИВАЕМЫХ МЕТРИК)
# =====================================================================
def analyze_light(seq_id, table_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # 7-я метрика: простая быстрая автокорреляция Лаг 1
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        cov = np.mean(x_lag * y_lag)
        ac_lag1 = float(cov / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else:
        ac_lag1 = 0.0

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    return {
        "ID": f'="{seq_id}"',
        "Тип_Стола": table_name,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Среднее": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение": safe_num(std_val, 4),
        "Метрика_4_Минимум": safe_num(np.min(seq), 4),
        "Метрика_5_Максимум": safe_num(np.max(seq), 4),
        "Метрика_6_Аномалия_Шага": safe_num(step_anomaly, 4),
        "Метрика_7_Автокорреляция_Лаг1": safe_num(ac_lag1, 4)
    }

# =====================================================================
# ЗАПУСК КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛸 HASE v6.0-LIGHT: ФИКСАЦИЯ ПЕРВЕНСТВА В ЭРГОДИЧЕСКИХ БИЛЛИАРДАХ")
    print("="*60)
    
    mega_dataset = []
    start_time = time.time()
    
    for t_type in TABLE_TYPES:
        print(f"🪸 Синтезируем столы класса: {t_type}...")
        for i in range(ROWS_PER_TABLE):
            row_id = f"{t_type.upper()}_ORBIT_{i+1}"
            
            # 1. Генерируем траекторию отскоков
            raw_seq = generate_billiard_trajectory(t_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Считаем 7 базовых фич
            analysis = analyze_light(row_id, t_type, raw_seq)
            analysis["Сырой_Ряд_Импульсов"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_dataset.append(analysis)
            
        print(f"   📊 Класс {t_type} успешно собран.")

    # Сохраняем все в один CSV-файл
    df = pd.DataFrame(mega_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*60)
    print("👑 АТЛАС ЭРГОДИЧЕСКОГО БИЛЛИАРДНОГО ХАОСА УСПЕШНО ЗАПЕЧАТАН!")
    print(f"📊 Всего сгенерировано: {len(df)} орбит (4 вида столов по {ROWS_PER_TABLE} строк).")
    print(f"📂 Готовый файл: {OUTPUT_FILE}")
    print(f"⏱️ Время работы процессора: {round(time.time() - start_time, 2)} сек.")
    print("="*60)
