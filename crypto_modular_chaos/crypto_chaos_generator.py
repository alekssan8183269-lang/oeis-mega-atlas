import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО КРИПТО-КОНВЕЙЕРА
# =====================================================================
SEQ_LENGTH = 110            # Длина финансового временного ряда
ROWS_PER_MODEL = 35         # Количество симуляций на каждую рыночную модель
OUTPUT_FILE = "crypto_market_volatility_dataset.csv"

# Новые паттерны крипто-рынка вместо криптографических модулей
MARKET_MODELS = ["Crypto_Bull_Trend", "Crypto_Bear_Crash", "HFT_Market_Flat", "Whale_Pump_Chaos"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР МОДЕЛЕЙ ВОЛАТИЛЬНОСТИ КРИПТО-РЫНКА
# =====================================================================
def generate_crypto_market_series(model_type, length, row_idx):
    """Генерирует временные ряды, моделирующие различные состояния крипто-рынка"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 41)
    
    time_series = []
    
    if model_type == "Crypto_Bull_Trend":
        # Бычий тренд с логарифмическим ростом и ценовыми откатами
        price = 100.0
        for t in range(length):
            # Логарифмический дрейф вверх + случайное блуждание
            drift = 1.5 * np.log10(t + 2)
            shock = np.random.normal(0.2, 1.2)
            price += drift + shock
            time_series.append(max(0.1, price))
            
    elif model_type == "Crypto_Bear_Crash":
        # Медвежий обвал: каскадная паника, экспоненциальное падение
        price = 1000.0
        for t in range(length):
            # Паника усиливается со временем (каскадный эффект)
            panic_factor = 0.01 * min(t, 40)
            shock = np.random.normal(-2.0 - panic_factor, 3.0)
            # Изредка отскоки "дохлой кошки"
            if np.random.rand() > 0.85:
                shock += np.random.exponential(5.0)
            price += shock
            # Имитация ликвидаций при сильном падении
            if price < 500 and np.random.rand() > 0.7:
                price *= 0.85 
            time_series.append(max(0.1, price))
            
    elif model_type == "HFT_Market_Flat":
        # Высокочастотный шум торговых роботов во флэте (Mean Reversion)
        base_price = 50.0
        price = base_price
        for _ in range(length):
            # Возврат к среднему значению + микрошум
            drift = 0.3 * (base_price - price)
            noise = np.random.normal(0, 0.5)
            price += drift + noise
            time_series.append(max(0.1, price))
            
    else: # Whale_Pump_Chaos
        # Манипуляции крупных китов: резкий вертикальный памп и жесткий дамп
        price = 10.0
        pump_start = length // 4
        dump_start = length // 2
        for t in range(length):
            if t < pump_start:
                # Накопление позиции (тихий флэт)
                shock = np.random.normal(0, 0.1)
            elif pump_start <= t < dump_start:
                # Вертикальный агрессивный памп
                shock = np.random.exponential(4.0) + np.random.normal(1.0, 0.5)
            else:
                # Слив об толпу (жёсткий дамп) и хаос
                shock = -np.random.exponential(5.0) - np.random.normal(1.5, 1.0)
            
            price += shock
            time_series.append(max(0.1, price))

    # Накладываем 1% биржевого шума (проскальзывание ордеров, спреды)
    raw_array = np.array(time_series, dtype=float)
    noise_layer = np.random.normal(0, np.mean(raw_array) * 0.01, size=length)
    return np.abs(raw_array + noise_layer)

# =====================================================================
# ШАГ 2: КРИПТО-АНАЛИЗАТОР (9 МЕТРИК) — БЕЗ ИЗМЕНЕНИЙ
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
    sign_profile = np.where(diffs > 0, 1, 0)
    p1 = np.sum(sign_profile) / max(1, len(sign_profile))
    p0 = 1.0 - p1
    binary_sign_entropy = float(-(p1 * math.log2(p1 + 1e-12) + p0 * math.log2(p0 + 1e-12)))

    # 9-я метрика: Девиация первого знака (Лайт-тест закона Бенфорда)
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
        "Рыночная_Модель": algo_name,
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
    print("🛸 HASE v1.0-FINANCE: СИМУЛЯЦИЯ РЫНОЧНОЙ ВОЛАТИЛЬНОСТИ")
    print("="*60)
    
    mega_dataset = []
    start_time = time.time()
    
    for m_type in MARKET_MODELS:
        print(f"📈 Симулируем ценовые ряды для паттерна: {m_type}...")
        for i in range(ROWS_PER_MODEL):
            row_id = f"{m_type.upper()}_MARKET_{i+1}"
            
            # 1. Генерируем реальную экономическую модель крипто-рынка
            raw_seq = generate_crypto_market_series(m_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Вычисляем 9 базовых фич (они перемалывают ряды без изменений)
            analysis = analyze_crypto_light(row_id, m_type, raw_seq)
            analysis["Сырой_Финансовый_Поток"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_dataset.append(analysis)
            
        print(f"   📊 Модель {m_type} успешно обработана.")

    # Запись результатов в файл
    df = pd.DataFrame(mega_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*60)
    print(f"👑 КРИПТО-МАРКЕТ СГЕНЕРИРОВАН!")
    print(f"📊 Всего сгенерировано: {len(df)} финансовых рядов.")
    print(f"📂 Ищи файл: {OUTPUT_FILE}")
    print(f"⏱️ Время симуляции: {round(time.time() - start_time, 2)} сек.")
    print("="*60)

