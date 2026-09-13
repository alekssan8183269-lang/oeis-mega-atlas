import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО КОНВЕЙЕРА ДЛЯ КУЧИ ПЕСКА
# =====================================================================
SEQ_LENGTH = 100            # Количество зафиксированных лавин в ряду
ROWS_PER_GRID = 35          # Количество уникальных рядов на каждую форму сосуда
OUTPUT_FILE = "sandpile_criticality_light_dataset.csv"

# Формы сосудов / типы сеток для кучи песка
GRID_TYPES = ["Square_Grid_15x15", "Circular_Vessel", "Rectangular_Chamber", "Fractal_Border_Grid"]

def safe_num(val, ndigits=4):
    """Защита от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР ЛАВИН САМООРГАНИЗОВАННОЙ КРИТИЧНОСТИ
# =====================================================================
def generate_sandpile_avalanches(grid_type, length, row_idx):
    """Симулирует физику падения песчинок и считает размеры лавин при обрушении кучи"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 31)
    
    # Создаем сетку 20х20 с запасом
    size = 20
    grid = np.zeros((size, size), dtype=int)
    
    time_series = []
    
    # Запускаем симуляцию до тех пор, пока не наберем нужное количество лавин
    while len(time_series) < length:
        # Капаем песчинку в случайное место (или в центр в зависимости от геометрии)
        if grid_type == "Circular_Vessel":
            # Капаем ближе к центру круга
            r, theta = np.random.uniform(0, 5), np.random.uniform(0, 2*np.pi)
            cx = int(size/2 + r * np.cos(theta))
            cy = int(size/2 + r * np.sin(theta))
        elif grid_type == "Square_Grid_15x15":
            cx, cy = np.random.randint(3, 17), np.random.randint(3, 17)
        else:
            cx, cy = int(size/2), int(size/2) # В центр для остальных типов
            
        grid[cx, cy] += 1
        
        # Физика лавинного обрушения (топплинг)
        avalanche_size = 0
        while np.any(grid >= 4):
            # Находим все нестабильные ячейки
            overflown = np.where(grid >= 4)
            for x, y in zip(overflown[0], overflown[1]):
                # Проверяем границы геометрии (сброс песка со стола)
                if x <= 0 or x >= size-1 or y <= 0 or y >= size-1:
                    grid[x, y] = 0
                    continue
                    
                # Ограничиваем геометрию сосуда
                if grid_type == "Circular_Vessel" and (x-size/2)**2 + (y-size/2)**2 > 64:
                    grid[x, y] = 0
                    continue
                
                # Обрушение песка на 4 соседа
                grid[x, y] -= 4
                grid[x+1, y] += 1
                grid[x-1, y] += 1
                grid[x, y+1] += 1
                grid[x, y-1] += 1
                avalanche_size += 1
                
        # Регистрируем лавину, если она произошла
        if avalanche_size > 0:
            # Добавляем 1% физического шума застревания песчинок
            shimmered_size = avalanche_size + np.random.normal(0, avalanche_size * 0.01)
            time_series.append(abs(shimmered_size))
            
    return np.array(time_series[:length], dtype=float)

# =====================================================================
# ШАГ 2: АНАЛИЗАТОР (РОВНО 8  МЕТРИК)
# =====================================================================
def analyze_sandpile_light(seq_id, grid_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # 7-я метрика: Автокорреляция Лаг 1
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # 8-я метрика: Простейший наклон спектра (замена тяжелого FFT для оценки 1/f шума)
    # Показывает скорость затухания амплитуд разностей
    if len(diffs) > 1:
        trend_slope, _ = np.polyfit(np.arange(len(diffs)), np.abs(diffs), 1)
        spectral_slope_proxy = float(trend_slope)
    else: spectral_slope_proxy = 0.0

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    return {
        "ID": f'="{seq_id}"',
        "Форма_Сетки": grid_name,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Средний_Размер_Лавины": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение": safe_num(std_val, 4),
        "Метрика_4_Минимальная_Лавина": safe_num(np.min(seq), 4),
        "Метрика_5_Максимальная_Лавина": safe_num(np.max(seq), 4),
        "Метрика_6_Аномалия_Обрушения": safe_num(step_anomaly, 4),
        "Метрика_7_Автокорреляция_Лаг1": safe_num(ac_lag1, 4),
        "Метрика_8_Прокси_1_f_Шума": safe_num(spectral_slope_proxy, 6)
    }

# =====================================================================
# ЗАПУСК КОНВЕЙЕРА ПЕСКА
# =====================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛸 HASE v6.0-SANDPILE: ГЕНЕРАЦИЯ НИШИ МОДЕЛЕЙ КУЧИ ПЕСКА")
    print("="*60)
    
    mega_dataset = []
    start_time = time.time()
    
    for g_type in GRID_TYPES:
        print(f"🪸 Симулируем лавины на геометрии: {g_type}...")
        for i in range(ROWS_PER_GRID):
            row_id = f"{g_type.upper()}_SANDPILE_{i+1}"
            
            # 1. Генерируем временной ряд обрушений
            raw_seq = generate_sandpile_avalanches(g_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Препарируем через 8 неубиваемых фич
            analysis = analyze_sandpile_light(row_id, g_type, raw_seq)
            analysis["Сырой_Ряд_Лавин"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_dataset.append(analysis)
            
        print(f"   📊 Геометрия {g_type} полностью просчитана.")

    # Запись в CSV
    df = pd.DataFrame(mega_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*60)
    print(f"👑 АТЛАС ПЕСКА СОЗДАН УСПЕШНО!")
    print(f"📊 Всего сгенерировано: {len(df)} рядов лавин.")
    print(f"📂 Готовый файл: {OUTPUT_FILE}")
    print(f"⏱️ Общее время симуляции: {round(time.time() - start_time, 2)} сек.")
    print("="*60)
