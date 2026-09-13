import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СТРУННОГО КОНВЕЙЕРА (КАЛАБИ-ЯУ)
# =====================================================================
SEQ_LENGTH = 110            # Длина ряда (количество квантовых шагов струны)
ROWS_PER_MANIFOLD = 35      # Сколько уникальных орбит генерировать на каждое многообразие
OUTPUT_FILE = "calabi_yau_string_trajectories.csv"

# Типы (алгебраические формы) пространств Калаби-Яу
MANIFOLD_TYPES = ["Quintic_Hypersurface_6D", "Tian_Yau_Manifold", "Schimmrig_Fractal_Fold", "K3_Surface_Projection"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР ОДНОМЕРНЫХ СЛЕДОВ ГЕОДЕЗИЧЕСКИХ В 6D ПРОСТРАНСТВАХ
# =====================================================================
def generate_calabi_yau_trajectory(manifold_type, length, row_idx):
    """Симулирует движение суперструны, скрученной внутри 6-мерного многообразия"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 79)
    
    # Инициализируем 6 пространственных координат струны (X1, X2, X3, X4, X5, X6)
    coords = np.array([0.1, 0.2, 0.1, -0.1, 0.3, 0.0], dtype=float)
    
    # Направление 6D вектора скорости
    angles = np.random.uniform(0, 2 * np.pi, 5)
    vx = np.array([
        math.cos(angles[0]),
        math.sin(angles[0]) * math.cos(angles[1]),
        math.sin(angles[0]) * math.sin(angles[1]) * math.cos(angles[2]),
        math.sin(angles[0]) * math.sin(angles[1]) * math.sin(angles[2]) * math.cos(angles[3]),
        math.sin(angles[0]) * math.sin(angles[1]) * math.sin(angles[2]) * math.sin(angles[3]) * math.cos(angles[4]),
        math.sin(angles[0]) * math.sin(angles[1]) * math.sin(angles[2]) * math.sin(angles[3]) * math.sin(angles[4])
    ])
    
    time_series = []
    dt = 0.05
    
    # Комплексный параметр деформации формы Калаби-Яу (модули струны)
    psi = np.random.uniform(0.2, 0.8)
    
    for step in range(length):
        # Движение по геодезической линии
        coords += vx * dt
        
        # Симулируем нелинейное "отражение" и скручивание от комплексных гиперповерхностей
        if manifold_type == "Quintic_Hypersurface_6D":
            # Квинтика Ферма: сумма координат в 5-й степени равна константе
            f_val = np.sum(coords**5) - psi
            if abs(f_val) > 1.5:
                vx = -vx + np.random.normal(0, 0.02, 6) # Удар о многообразие
                coords -= vx * dt
        elif manifold_type == "Tian_Yau_Manifold":
            # Пространство Тяня-Яу (асимметричное скручивание слоев)
            f_val = (coords[0]**3 + coords[1]**3 + coords[2]**3) * (coords[3]**3 + coords[4]**3 + coords[5]**3) - psi
            if abs(f_val) > 2.0:
                vx = -vx + np.random.normal(0, 0.02, 6)
                coords -= vx * dt
        elif manifold_type == "Schimmrig_Fractal_Fold":
            # Фрактальное расслоение Шиммрига (зеркальная симметрия струн)
            f_val = np.sum(coords[::2]**4) - np.sum(coords[1::2]**4) - psi
            if abs(f_val) > 1.2:
                vx = -vx + np.random.normal(0, 0.01, 6)
                coords -= vx * dt
        else: # K3_Surface_Projection
            # Поверхность К3, развернутая в гиперкёлерову метрику
            f_val = np.sum(coords**4) - psi
            if abs(f_val) > 1.0:
                vx = -vx + np.random.normal(0, 0.01, 6)
                coords -= vx * dt
                
        # Нормируем вектор 6D-скорости
        vx /= (np.linalg.norm(vx) + 1e-12)
        
        # Снимаем одномерный физический след: Квантовое евклидово расстояние струны от сингулярного ядра
        string_tension_distance = float(np.linalg.norm(coords))
        time_series.append(string_tension_distance)
        
    # Впрыскиваем 1% квантового шума супергравитации (дефекты планковского масштаба)
    raw_array = np.array(time_series, dtype=float)
    return np.abs(raw_array + np.random.normal(0, 0.01, size=length))

# =====================================================================
# ШАГ 2: СТРУННЫЙ СПЕКТРОМЕТР (РОВНО 8 ВЫСШИХ МЕТРИК)
# =====================================================================
def analyze_calabi_yau_light(seq_id, manifold_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # 7-я метрика: Быстрый Лаг 1 автокорреляции
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # 8-я метрика: Извилистость струнного следа (отношение разброса к среднему шагу)
    # Показывает, насколько сильно 6D геометрия спрессовала витки струны
    if len(diffs) > 0:
        string_tortuosity_proxy = float(np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-12))
    else: string_tortuosity_proxy = 1.0

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    # Высший ИИ-Вердикт
    if string_tortuosity_proxy > 1.8:
        verdict = "Hyper-Folded Calabi-Yau Core"
    else:
        verdict = "Symmetric Topological String Orbit"

    return {
        "ID": f'="{seq_id}"',
        "Тип_Многообразия_Калаби_Яу": manifold_name,
        "ИИ_Струнный_Вердикт": verdict,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Средний_Радиус_Струны": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение": safe_num(std_val, 4),
        "Метрика_4_Минимум": safe_num(np.min(seq), 4),
        "Метрика_5_Максимум": safe_num(np.max(seq), 4),
        "Метрика_6_Аномалия_Квантового_Скачка": safe_num(step_anomaly, 4),
        "Метрика_7_Автокорреляция_Лаг1": safe_num(ac_lag1, 4),
        "Метрика_8_Коэффициент_Скрученности": safe_num(string_tortuosity_proxy, 4)
    }

# =====================================================================
# ЗАПУСК СТРУННОГО КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*70)
    print("🛸 HASE v6.0-STRINGS: ГГЕНЕРАЦИЯ ДВИЖЕНИЯ ЧАСТИЦЫ В ВЫСШИХ ПРОСТРАНСТВАХ КАЛАБИ-ЯУ")
    print("="*70)
    
    mega_string_dataset = []
    start_time = time.time()
    
    for m_type in MANIFOLD_TYPES:
        print(f"🪸 Запускаем суперструну внутрь многообразия: {m_type}...")
        for i in range(ROWS_PER_MANIFOLD):
            row_id = f"{m_type.upper()}_STRING_{i+1}"
            
            # 1. Симулируем 6D квантовую траекторию и сворачиваем в 1D
            raw_seq = generate_calabi_yau_trajectory(m_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Извлекаем 8 легких топологических параметров
            analysis = safe_analysis = analyze_calabi_yau_light(row_id, m_type, raw_seq)
            analysis["Сырой_След_Суперструны"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_string_dataset.append(analysis)
            
        print(f"   静态 Многообразие {m_type} успешно оцифровано в датасет.")

    # Запись в CSV
    df = pd.DataFrame(mega_string_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*70)
    print(f"👑  Калаби-Яу ряды созданы полета частиц!")
    print(f"📊 Всего оцифровано: {len(df)} одномерных квантовых следов 6D-пространств.")
    print(f"📂 Готовый файл: {OUTPUT_FILE}")
    print(f"⏱️ Время работы процессора: {round(time.time() - start_time, 2)} сек.")
    print("="*70)
