import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО КВАНТОВОГО КОНВЕЙЕРА
# =====================================================================
SEQ_LENGTH = 110            # Длина одномерного квантового следа
ROWS_PER_SPACE = 35         # Сколько уникальных торсионных траекторий крутить
OUTPUT_FILE = "noncommutative_geometry_light_dataset.csv"

# Типы некоммутативных пространств и деформаций
SPACE_TYPES = ["Connes_Quantum_Torus", "Moyal_Deformed_Plane", "Snyder_Snyder_Space", "Torsion_Spin_Fold"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР НЕКОММУТАТИВНЫХ КВАНТОВЫХ ТРАЕКТОРИЙ
# =====================================================================
def generate_noncommutative_trace(space_type, length, row_idx):
    """Симулирует пошаговое смещение частицы в пространстве со сдвигом коммутации"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 53)
    
    time_series = []
    x, y = 1.0, 1.0
    
    # Параметр некоммутативности (квантовая постоянная деформации)
    theta = np.random.uniform(0.1, 0.5)
    
    for step in range(length):
        # Обычный шаг
        angle = np.random.uniform(0, 2 * np.pi)
        dx, dy = np.cos(angle), np.sin(angle)
        
        if space_type == "Connes_Quantum_Torus":
            # Квантовый тор Конна: некоммутативный фазовый сдвиг при каждом шаге
            x += dx
            y += dy + theta * math.sin(x)
        elif space_type == "Moyal_Deformed_Plane":
            # Мояловская деформация: перекрестное перемножение координат ломает коммутативность
            x += dx - theta * y * 0.1
            y += dy + theta * x * 0.1
        elif space_type == "Snyder_Snyder_Space":
            # Пространство Снайдера: масштаб шага зависит от квадрата расстояния (Лоренц-ковариантность)
            r2 = x**2 + y**2
            x += dx * (1.0 + theta * r2 * 0.01)
            y += dy * (1.0 + theta * r2 * 0.01)
        else: # Torsion_Spin_Fold
            # Торсионное закручивание (спин-орбитальный микроскопический дрейф)
            x += dx
            y += dy
            spin = math.atan2(y, x)
            x += theta * math.cos(spin * 3)
            
        # Записываем в качестве одномерного ряда квадрат нормированного квантового импульса
        quantum_momentum = math.sqrt(x**2 + y**2)
        time_series.append(quantum_momentum)
        
    # Накладываем 1% физического белого шума декогеренции поля
    raw_array = np.array(time_series, dtype=float)
    noise_layer = np.random.normal(0, 0.01, size=length)
    return np.abs(raw_array + noise_layer)

# =====================================================================
# ШАГ 2: КВАНТОВЫЙ АНАЛИЗАТОР (8 МЕТРИК)
# =====================================================================
def analyze_noncommutative_light(seq_id, space_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # 7-я метрика: Быстрый Лаг 1 автокорреляции
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # 8-я метрика: Коэффициент квантовых флуктуаций (вариация локального шага разностей)
    # Имитирует "торсионное трение пены" на микроуровне
    if len(diffs) > 1:
        quantum_foam_friction = float(np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-12))
    else: quantum_foam_friction = 0.0

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    return {
        "ID": f'="{seq_id}"',
        "Тип_Пространства": space_name,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Средний_Квантовый_Импульс": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение": safe_num(std_val, 4),
        "Метрика_4_Минимум": safe_num(np.min(seq), 4),
        "Метрика_5_Максимум": safe_num(np.max(seq), 4),
        "Метрика_6_Аномалия_Скачка": safe_num(step_anomaly, 4),
        "Метрика_7_Автокорреляция_Лаг1": safe_num(ac_lag1, 4),
        "Метрика_8_Трение_Квантовой_Пены": safe_num(quantum_foam_friction, 4)
    }

# =====================================================================
# ЗАПУСК КВАНТОВОГО КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛸 HASE v6.0-NONCOMMUTATIVE: ФИКСАЦИЯ РЯДОВ В КВАНТОВОЙ ГЕОМЕТРИИ")
    print("="*60)
    
    mega_dataset = []
    start_time = time.time()
    
    for s_type in SPACE_TYPES:
        print(f"🪸 Симулируем квантовый след в пространстве: {s_type}...")
        for i in range(ROWS_PER_SPACE):
            row_id = f"{s_type.upper()}_QUANTUM_{i+1}"
            
            # 1. Генерируем некоммутативную траекторию
            raw_seq = generate_noncommutative_trace(s_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Прогоняем через 8 легких фич
            analysis = analyze_noncommutative_light(row_id, s_type, raw_seq)
            analysis["Сырой_Квантовый_След"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_dataset.append(analysis)
            
        print(f"   📊 Пространство {s_type} полностью запечатано.")

    # Запись в CSV
    df = pd.DataFrame(mega_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*60)
    print(f"👑 КВАНТОВАЯ ПЛОЩАДКАРЯДОВ СГЕНЕРИРОВАНА!")
    print(f"📊 Всего сгенерировано: {len(df)} некоммутативных волновых рядов.")
    print(f"📂 Файл сохранен: {OUTPUT_FILE}")
    print(f"⏱️ Время работы процессора: {round(time.time() - start_time, 2)} сек.")
    print("="*60)
