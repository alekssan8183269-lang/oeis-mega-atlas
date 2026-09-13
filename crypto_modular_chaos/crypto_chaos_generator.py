import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО КРИПТО-КОНВЕЙЕРА
# =====================================================================
SEQ_LENGTH = 110            # Длина хаотической крипто-орбиты
ROWS_PER_PRIME = 35         # Сколько уникальных ключей генерировать на модуль
OUTPUT_FILE = "crypto_modular_chaos_light_dataset.csv"

# Наборы криптографических модулей (большие простые числа и алгоритмы)
ALGO_TYPES = ["Modular_Elliptic_31231", "LCM_Asymmetric_65537", "Fermat_Prime_Fold", "Mersenne_Pseudo_Chaos"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР МОДУЛЯРНЫХ ОРБИТ И КРИПТОГРАФИЧЕСКОГО ХАОСА
# =====================================================================
def generate_crypto_modular_chaos(algo_type, length, row_idx):
    """Генерирует псевдохаотические орбиты на конечных алгебраических полях"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 41)
    
    time_series = []
    
    if algo_type == "Modular_Elliptic_31231":
        # Итерация кубического многочлена (тип эллиптической кривой) по модулю P
        P = 31231
        x = np.random.randint(100, 5000)
        a, b = 7, 11
        for _ in range(length):
            x = (x**3 + a*x + b) % P
            time_series.append(float(x) / P) # Нормируем к 0-1
            
    elif algo_type == "LCM_Asymmetric_65537":
        # Алгоритм на основе простого числа Ферма F4
        P = 65537
        x = np.random.randint(500, 60000)
        multiplier = 48271
        for _ in range(length):
            x = (x * multiplier) % P
            time_series.append(float(x) / P)
            
    elif algo_type == "Fermat_Prime_Fold":
        # Двумерное скручивание знаков по модулю 10007
        P = 10007
        x = np.random.randint(10, P)
        for _ in range(length):
            x = (x**2 - 2) % P
            if x == 0: x = np.random.randint(10, P)
            time_series.append(float(x) / P)
            
    else: # Mersenne_Pseudo_Chaos
        # Псевдо-мерсеннов узор со сдвигом битов (XOR-shift аналог)
        P = 524287 # 2^19 - 1
        x = np.random.randint(1000, P)
        for _ in range(length):
            x ^= (x << 13) % P
            x ^= (x >> 17) % P
            x ^= (x << 5) % P
            time_series.append(float(x % 10000) / 10000.0)

    # Накладываем 1% физического шума искажения канала связи (эмуляция перехвата сырого сигнала)
    raw_array = np.array(time_series, dtype=float)
    noise_layer = np.random.normal(0, 0.01, size=length)
    return np.abs(raw_array + noise_layer)

# =====================================================================
# ШАГ 2: КРИПТО-АНАЛИЗАТОР ( 9 МЕТРИК)
# =====================================================================
def analyze_crypto_light(seq_id, algo_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # 7-я метрика: Быстрый Лаг 1 автокорреляции
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # 8-я метрика: Простейший маркер симметрии (энтропия знаков приращений)
    # Показывает, насколько сбалансированы шаги вверх-вниз в крипто-потоке
    sign_profile = np.where(diffs > 0, 1, 0)
    p1 = np.sum(sign_profile) / max(1, len(sign_profile))
    p0 = 1.0 - p1
    binary_sign_entropy = float(-(p1 * math.log2(p1 + 1e-12) + p0 * math.log2(p0 + 1e-12)))

    # 9-я метрика: Девиация первого знака (Лайт-тест закона Бенфорда)
    # Показывает скрытые перекосы в мантиссе модулярных генераторов
    first_digits = [int(str(abs(x)).replace('.', '').lstrip('0')[0]) for x in seq if abs(x) > 1e-4]
    if first_digits:
        counts = np.bincount(first_digits, minlength=10)[1:10]
        probs = counts / np.sum(counts)
        benford_ideal = np.log10(1 + 1/np.arange(1, 10))
        benford_deviation_proxy = float(np.sum((probs - benford_ideal) ** 2))
    else: benford_deviation_proxy = 1.0

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    return {
        "ID": f'="{seq_id}"',
        "Крипто_Алгоритм": algo_name,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Среднее": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение": safe_num(std_val, 4),
        "Метрика_4_Минимум": safe_num(np.min(seq), 4),
        "Метрика_5_Максимум": safe_num(np.max(seq), 4),
        "Метрика_6_Аномалия_Переходов": safe_num(step_anomaly, 4),
        "Метрика_7_Автокорреляция_Лаг1": safe_num(ac_lag1, 4),
        "Метрика_8_Энтропия_Направлений": safe_num(binary_sign_entropy, 4),
        "Метрика_9_Прокси_Бенфорда": safe_num(benford_deviation_proxy, 6)
    }

# =====================================================================
# ЗАПУСК КРИПТО-КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛸 HASE v6.0-CRYPTO: ЗАПЕЧАТЫВАНИЕ КРИПТОГРАФИЧЕСКОГО ХАОСА")
    print("="*60)
    
    mega_dataset = []
    start_time = time.time()
    
    for a_type in ALGO_TYPES:
        print(f"🪸 Генерируем модулярные орбиты для: {a_type}...")
        for i in range(ROWS_PER_PRIME):
            row_id = f"{a_type.upper()}_CRYPTO_{i+1}"
            
            # 1. Генерируем псевдослучайную криптографическую траекторию
            raw_seq = generate_crypto_modular_chaos(a_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Вычисляем 9 базовых фич
            analysis = analyze_crypto_light(row_id, a_type, raw_seq)
            analysis["Сырой_Крипто_Поток"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_dataset.append(analysis)
            
        print(f"   📊 Алгоритм {a_type} успешно отработал.")

    # Запись результатов в файл
    df = pd.DataFrame(mega_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*60)
    print(f"👑 КРИПТО-ПОЛЯНА СГЕНЕРИРОВАНнаа!")
    print(f"📊 Всего сгенерировано: {len(df)} орбит по модулю простых чисел.")
    print(f"📂 Ищи файл: {OUTPUT_FILE}")
    print(f"⏱️ Скорость процессора: {round(time.time() - start_time, 2)} сек.")
    print("="*60)
