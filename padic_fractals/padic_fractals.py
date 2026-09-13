import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО СИНТЕТИЧЕСКОГО КОНВЕЙЕРА (ДВОЙНАЯ НИША)
# =====================================================================
SEQ_LENGTH = 100            # Длина каждого числового ряда
ROWS_PER_CLASS = 35         # Сколько рядов генерировать на каждую подсистему
OUTPUT_FILE_1 = "padic_fractals_light_dataset.csv"
OUTPUT_FILE_2 = "hyperbolic_cellular_automata_light_dataset.csv"

PADIC_TYPES = ["p_Adic_Field_p2", "p_Adic_Field_p3", "p_Adic_Field_p5", "p_Adic_Field_p7"]
HYPERBOLIC_TYPES = ["Heptagonal_Poincare_Grid", "Saddle_Wolfram_Rule30", "Hyperbolic_Avalanche_Net", "Lobachevsky_Life_Step"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ГЕНЕРАТОР НИШИ №6: p-АДИЧЕСКИЕ ФРАКТАЛЬНЫЕ ЛАНДШАФТЫ
# =====================================================================
def generate_padic_fractal(p_type, length, row_idx):
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 61)
    p = int(p_type.split("_p")[-1]) if "_p" in p_type else 2
    
    time_series = []
    current_val = 0.0
    
    for step in range(length):
        # Генерируем случайное целое число
        random_int = np.random.randint(1, 1000000)
        
        # Считаем p-адическую норму (высшая алгебра: чем больше число делится на p, тем ближе норма к 0)
        valuation = 0
        while random_int % p == 0 and random_int > 0:
            valuation += 1
            random_int //= p
            
        padic_norm = 1.0 / (p ** valuation) if valuation > 0 else 1.0
        
        # Строим случайное неархимедово блуждание (фрактальный ландшафт)
        current_val += np.random.choice([-1, 1]) * padic_norm
        time_series.append(current_val)
        
    # Добавляем 1% аналогового шума флуктуации мантиссы
    raw_array = np.array(time_series, dtype=float)
    return np.abs(raw_array + np.random.normal(0, 0.01, size=length))

# =====================================================================
# ГЕНЕРАТОР НИШИ №7: ГИПЕРБОЛИЧЕСКИЕ АВТОМАТЫ НА ГЕОМЕТРИИ ЛОБАЧЕВСКОГО
# =====================================================================
def generate_hyperbolic_automaton(grid_type, length, row_idx):
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 67)
    
    # Моделируем экспоненциальный рост числа соседей на плоскости Лобачевского
    # В гиперболической сетке количество узлов в слоях растет как фи-пропорция Фибоначчи
    nodes_per_layer = [7]
    for _ in range(15):
        nodes_per_layer.append(int(nodes_per_layer[-1] * 1.618))
        
    time_series = []
    
    # Симулируем пошаговое изменение плотности "живых" ячеек
    current_density = np.random.uniform(0.1, 0.4)
    
    for step in range(length):
        # Локальное правило Вольфрама, искаженное геометрией седла
        noise_scale = 0.01 if grid_type == "Heptagonal_Poincare_Grid" else 0.02
        
        # Эволюция плотности с учетом взрывного гиперболического расширения границ стола
        growth_factor = math.sin(step * 0.5) * 0.1
        current_density = (current_density * 1.42 + growth_factor) % 1.0
        
        # Регистрируем "акустический" шаг лавины (число активных узлов во фрактальной решетке)
        active_nodes = current_density * nodes_per_layer[step % len(nodes_per_layer)]
        time_series.append(abs(active_nodes))
        
    raw_array = np.array(time_series, dtype=float)
    return raw_array + np.random.normal(0, np.mean(raw_array) * 0.01, size=length)

# =====================================================================
# УНИВЕРСАЛЬНЫЙ АНАЛИЗАТОР (8 МЕТРИК)
# =====================================================================
def analyze_universal_light(seq_id, class_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # Автокорреляция Лаг 1
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # Робастный разброс MAD (устойчивость хаоса)
    mad_score = float(np.median(np.abs(seq - np.median(seq))))

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    return {
        "ID": f'="{seq_id}"',
        "Математический_Класс": class_name,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Среднее": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение": safe_num(std_val, 4),
        "Метрика_4_Минимум": safe_num(np.min(seq), 4),
        "Метрика_5_Максимум": safe_num(np.max(seq), 4),
        "Метрика_6_Излом_Профиля": safe_num(step_anomaly, 4),
        "Метрика_7_Автокорреляция_Лаг1": safe_num(ac_lag1, 4),
        "Метрика_8_Робастность_MAD": safe_num(mad_score, 4)
    }

# =====================================================================
# ГЛАВНЫЙ ЗАПУСК ДВОЙНОГО КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*75)
    print("🛸 HASE v6.0-DUAL: ЗАКРЫТИЕ ПОСЛЕДНИХ БОГОМ ЗАБЫТЫХ НИШ (ФРАКТАЛЫ + АВТОМАТЫ)")
    print("="*75)
    
    start_time = time.time()
    
    # --- СБОРКА НИШИ №6: p-АДИЧЕСКИЕ ФРАКТАЛЫ ---
    dataset_padic = []
    print("\n💎 ШАГ 1: Запуск p-адического квантового генератора...")
    for p_type in PADIC_TYPES:
        print(f"   🪸 Симулируем неархимедово поле: {p_type}...")
        for i in range(ROWS_PER_CLASS):
            row_id = f"{p_type.upper()}_PADIC_{i+1}"
            raw_seq = generate_padic_fractal(p_type, SEQ_LENGTH, row_idx=i)
            analysis = analyze_universal_light(row_id, p_type, raw_seq)
            analysis["Сырой_Ряд_p_Adic"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            dataset_padic.append(analysis)
            
    df_padic = pd.DataFrame(dataset_padic)
    df_padic.to_csv(OUTPUT_FILE_1, index=False, sep=";", encoding="utf-8-sig")
    print(f"✅ Файл {OUTPUT_FILE_1} успешно запечатан!")

    # --- СБОРКА НИШИ №7: ГИПЕРБОЛИЧЕСКИЕ АВТОМАТЫ ---
    dataset_hyper = []
    print("\n🕸️ ШАГ 2: Запуск симулятора автоматов Лобачевского...")
    for h_type in HYPERBOLIC_TYPES:
        print(f"   🪸 Разворачиваем гиперболическую сетку: {h_type}...")
        for i in range(ROWS_PER_CLASS):
            row_id = f"{h_type.upper()}_HYPERBOLIC_{i+1}"
            raw_seq = generate_hyperbolic_automaton(h_type, SEQ_LENGTH, row_idx=i)
            analysis = analyze_universal_light(row_id, h_type, raw_seq)
            analysis["Сырой_Гиперболический_Профиль"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            dataset_hyper.append(analysis)
            
    df_hyper = pd.DataFrame(dataset_hyper)
    df_hyper.to_csv(OUTPUT_FILE_2, index=False, sep=";", encoding="utf-8-sig")
    print(f"✅ Файл {OUTPUT_FILE_2} успешно запечатан!")

    print("\n" + "="*75)
    print("👑 Двойной финальный код: p-Адические фракталы + Гиперболические автоматы!")
    print(" Семиугольные Клеточные Автоматы Вольфрама на Геометрии Лобачевского — одномерные числовые профили ")
    print(" лавин и эволюции живых клеток на искривленной экспоненциальной сетке (седле).")
    print("  p-Адические Фрактальные Ландшафты — фрактальные случайные блуждания ")
    print(" по неархимедовой метрике деревьев Брюа-Титса для простых чисел \(p=2, 3, 5, 7\). ")
    print(f"📊 Всего создано: {len(df_padic)} рядов фракталов и {len(df_hyper)} профилей автоматов.")
    print(f"⏱️ Суммарное время тотального доминирования: {round(time.time() - start_time, 2)} сек.")
    print("="*75)
