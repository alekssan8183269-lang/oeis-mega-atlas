import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО ТОПОЛОГИЧЕСКОГО КОНВЕЙЕРА
# =====================================================================
SEQ_LENGTH = 120            # Длина одномерного шага узла
ROWS_PER_KNOT = 35          # Сколько уникальных деформаций узла крутить
OUTPUT_FILE = "knot_topology_light_dataset.csv"

# Фундаментальные математические узлы
KNOT_TYPES = ["Trefoil_Knot_3_1", "Figure_Eight_4_1", "Solomon_Link_Cluster", "Toroidal_Chaos_5_2"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР ТРЕХМЕРНЫХ МАТЕМАТИЧЕСКИХ УЗЛОВ (Разворот 3D -> 1D)
# =====================================================================
def generate_knot_profile(knot_type, length, row_idx):
    """Генерирует одномерный шаг натяжения на основе 3D-геометрии узлов"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 47)
    
    # Сетка углового шага t
    t_vals = np.linspace(0, 2 * np.pi, length)
    time_series = []
    
    # Коэффициенты деформации (микро-натяжения узла в пространстве)
    shimmer = np.random.uniform(0.95, 1.05)
    
    for t in t_vals:
        if knot_type == "Trefoil_Knot_3_1":
            # Узел Трилистник (3_1)
            x = math.sin(t) + 2 * math.sin(2 * t) * shimmer
            y = math.cos(t) - 2 * math.cos(2 * t) * shimmer
            z = -math.sin(3 * t) * shimmer
        elif knot_type == "Figure_Eight_4_1":
            # Узел Восьмерка (4_1)
            x = (2 + math.cos(2 * t)) * math.cos(3 * t) * shimmer
            y = (2 + math.cos(2 * t)) * math.sin(3 * t) * shimmer
            z = math.sin(4 * t) * shimmer
        elif knot_type == "Solomon_Link_Cluster":
            # Зацепление Соломона (высший трилистный тор)
            x = math.sin(3 * t) * shimmer
            y = math.sin(t) + 1.5 * math.sin(2 * t)
            z = math.cos(t) - 1.5 * math.cos(2 * t)
        else: # Toroidal_Chaos_5_2
            # Скрученный тороидальный узел (5_2)
            x = math.sin(2 * t) * (2 + math.cos(5 * t)) * shimmer
            y = math.cos(2 * t) * (2 + math.cos(5 * t)) * shimmer
            z = math.sin(5 * t) * shimmer
            
        # Превращаем 3D-координаты в одномерный след: евклидово расстояние точки от центра масс
        radius_vector = math.sqrt(x**2 + y**2 + z**2)
        time_series.append(radius_vector)
        
    # Накладываем 1% теплового молекулярного шума деформации нити
    raw_array = np.array(time_series, dtype=float)
    noise_layer = np.random.normal(0, 0.01, size=length)
    return np.abs(raw_array + noise_layer)

# =====================================================================
# ШАГ 2: ТОПОЛОГИЧЕСКИЙ АНАЛИЗАТОР (8  МЕТРИК)
# =====================================================================
def analyze_knot_light(seq_id, knot_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # 7-я метрика: Быстрый Лаг 1 автокорреляции
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # 8-я метрика: Робастный разброс MAD (Медианное абсолютное отклонение)
    # Показывает жесткость "скруток" геометрии нити узла
    mad_score = float(np.median(np.abs(seq - np.median(seq))))

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    return {
        "ID": f'="{seq_id}"',
        "Математический_Узел": knot_name,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Средний_Радиус_Зацепления": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение": safe_num(std_val, 4),
        "Метрика_4_Минимум": safe_num(np.min(seq), 4),
        "Метрика_5_Максимум": safe_num(np.max(seq), 4),
        "Метрика_6_Излом_Нити": safe_num(step_anomaly, 4),
        "Метрика_7_Автокорреляция_Лаг1": safe_num(ac_lag1, 4),
        "Метрика_8_Жесткость_MAD": safe_num(mad_score, 4)
    }

# =====================================================================
# ЗАПУСК ТОПОЛОГИЧЕСКОГО КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛸 HASE v6.0-KNOTS: ГЕНЕРАЦИЯ РЯДОВ В ТЕОРИИ УЗЛОВ")
    print("="*60)
    
    mega_dataset = []
    start_time = time.time()
    
    for k_type in KNOT_TYPES:
        print(f"🪸 Заплетаем и сканируем узел класса: {k_type}...")
        for i in range(ROWS_PER_KNOT):
            row_id = f"{k_type.upper()}_KNOT_{i+1}"
            
            # 1. Разворачиваем геометрию узла в одномерный профиль
            raw_seq = generate_knot_profile(k_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Прогоняем через 8 легких фич
            analysis = analyze_knot_light(row_id, k_type, raw_seq)
            analysis["Сырой_Шаг_Узла"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_dataset.append(analysis)
            
        print(f"   📊 Узел {k_type} успешно запечатан в матрицу.")

    # Запись в CSV
    df = pd.DataFrame(mega_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*60)
    print(f"👑 ТОПОЛОГИЧЕСКАЯ ПОЛЯНА ОФИЦИАЛЬНО СГЕНЕРИРОВАННА!")
    print(f"📊 Всего сгенерировано: {len(df)} зацепленных одномерных траекторий.")
    print(f"📂 Файл сохранен: {OUTPUT_FILE}")
    print(f"⏱️ Время работы процессора: {round(time.time() - start_time, 2)} сек.")
    print("="*60)
