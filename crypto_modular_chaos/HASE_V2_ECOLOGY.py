import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО КРИПТО-КОНВЕЙЕРА HASE v7.0
# =====================================================================
SEQ_LENGTH = 110            # Длина финансового временного ряда
ROWS_PER_MODEL = 35         # Количество симуляций на каждую рыночную модель
OUTPUT_FILE = "hase_v7_market_ecology_dataset.csv"

# Обновленный набор моделей (Добавлены спящие рынки и шоковые пробуждения)
MARKET_MODELS = [
    "Crypto_Bull_Trend", 
    "Crypto_Bear_Crash", 
    "HFT_Market_Flat", 
    "Whale_Pump_Chaos",
    "Crypto_Hyper_Hype_Chaos",
    "Dormant_Zombie_Flat",       # <- Новый паттерн: Спящий/мертвый рынок
    "Abrupt_Awakening_Shock"     # <- Новый паттерн: Внезапное жесткое пробуждение
]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР ЭКОЛОГИИ РЫНКА (ЦЕНА + ОБЪЕМ)
# =====================================================================
def generate_crypto_market_ecology(model_type, length, row_idx):
    """Генерирует совмещенные временные ряды Цены и Объема для разных фаз рынка"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 41)
    
    prices = []
    volumes = []
    
    if model_type == "Crypto_Bull_Trend":
        price = 100.0
        for t in range(length):
            drift = 1.5 * np.log10(t + 2)
            shock = np.random.normal(0.2, 1.2)
            price += drift + shock
            prices.append(max(0.1, price))
            # На бычьем тренде объемы растут вместе с ценой
            volumes.append(max(10.0, np.random.exponential(100.0) + price * 5))
            
    elif model_type == "Crypto_Bear_Crash":
        price = 1000.0
        for t in range(length):
            panic_factor = 0.01 * min(t, 40)
            shock = np.random.normal(-2.0 - panic_factor, 3.0)
            if np.random.rand() > 0.85:
                shock += np.random.exponential(5.0)
            price += shock
            if price < 500 and np.random.rand() > 0.7:
                price *= 0.85 
            prices.append(max(0.1, price))
            # В моменты паники объемы торгов взрываются (капитуляция)
            volumes.append(max(50.0, np.random.exponential(500.0) * (1 + panic_factor)))
            
    elif model_type == "HFT_Market_Flat":
        base_price = 50.0
        price = base_price
        for _ in range(length):
            drift = 0.3 * (base_price - price)
            noise = np.random.normal(0, 0.5)
            price += drift + noise
            prices.append(max(0.1, price))
            # Стабильно высокие монотонные объемы от роботов
            volumes.append(max(1.0, np.random.normal(200.0, 20.0)))
            
    elif model_type == "Whale_Pump_Chaos":
        price = 10.0
        pump_start = length // 4
        dump_start = length // 2
        for t in range(length):
            if t < pump_start:
                shock = np.random.normal(0, 0.1)
                vol = np.random.uniform(5.0, 15.0) # Тихий закуп
            elif pump_start <= t < dump_start:
                shock = np.random.exponential(4.0) + np.random.normal(1.0, 0.5)
                vol = np.random.exponential(1000.0) # Вертикальный объем на пампе
            else:
                shock = -np.random.exponential(5.0) - np.random.normal(1.5, 1.0)
                vol = np.random.exponential(1500.0) # Огромный объем на сливе
            price += shock
            prices.append(max(0.1, price))
            volumes.append(max(0.1, vol))

    elif model_type == "Crypto_Hyper_Hype_Chaos":
        price = 20.0
        velocity = 0.1
        hype_sentiment = 1.0
        for t in range(length):
            hype_sentiment += 0.05 * velocity + math.sin(t * 0.15) * 0.2
            hype_sentiment = max(0.1, min(hype_sentiment, 15.0))
            shock = np.random.normal(0.1 * hype_sentiment, 0.5 * (hype_sentiment**1.2))
            if hype_sentiment > 8.0 and np.random.rand() > 0.8:
                shock += np.random.exponential(12.0)
            velocity = 0.7 * velocity + 0.3 * shock
            price += velocity
            if price > 150.0 and np.random.rand() > 0.75:
                price *= 0.4
                velocity = -abs(velocity) * 1.5
                hype_sentiment *= 0.2
            prices.append(max(0.1, price))
            # Объем завязан на квадратичный хайп
            volumes.append(max(1.0, np.random.exponential(10.0) * (hype_sentiment**2)))

    elif model_type == "Dormant_Zombie_Flat":
        # 💀 СПЯЩИЙ РЫНОК: Полный штиль неделями и месяцами
        price = 5.0
        for _ in range(length):
            # Цены почти не меняются. Изредка (в 5% случаев) кто-то совершает микро-сделку
            if np.random.rand() > 0.95:
                price += np.random.normal(0, 0.05)
                vol = np.random.uniform(0.1, 2.0)
            else:
                vol = 0.0 # Нет торгов, стакан пустой
            prices.append(max(0.01, price))
            volumes.append(vol)

    elif model_type == "Abrupt_Awakening_Shock":
        # ⚡ ВСПЫШКА ИЗ ТЕМНОТЫ: Спящий зомби-рынок внезапно взрывается новостью
        price = 5.0
        awaken_t = int(length * 0.7) # Пробуждение ближе к концу ряда
        
        for t in range(length):
            if t < awaken_t:
                # Спит
                if np.random.rand() > 0.95:
                    price += np.random.normal(0, 0.02)
                    vol = np.random.uniform(0.1, 1.0)
                else:
                    vol = 0.0
            else:
                # ВЗРЫВ: Нелинейный ценовой шок и приток колоссальных объемов
                price_step = (t - awaken_t) ** 1.8
                price += np.random.exponential(2.0 + price_step * 0.1)
                vol = np.random.exponential(5000.0)
                
            prices.append(max(0.01, price))
            volumes.append(vol)

    # Микро-шум проскальзывания на финальные массивы
    p_array = np.abs(np.array(prices, dtype=float) + np.random.normal(0, np.mean(prices) * 0.005, size=length))
    v_array = np.abs(np.array(volumes, dtype=float) + np.random.normal(0, max(1.0, np.mean(volumes) * 0.005), size=length))
    
    return p_array, v_array

# =====================================================================
# ШАГ 2: КРИПТО-АНАЛИЗАТОР (9 МЕТРИК) — ПЕРЕМАЛЫВАЕТ ЦЕНОВЫЕ РЯДЫ
# =====================================================================
def analyze_crypto_light(seq_id, model_name, prices, volumes):
    n_len = len(prices)
    mean_val = np.mean(prices)
    std_val = np.std(prices) + 1e-8
    diffs = np.diff(prices)
    
    # 7-я метрика: Быстрый Лаг 1 автокорреляции
    if len(prices) > 1:
        x_lag, y_lag = prices[:-1] - np.mean(prices[:-1]), prices[1:] - np.mean(prices[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(prices[:-1]) * np.std(prices[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # 8-я метрика: Энтропия знаков приращений
    sign_profile = np.where(diffs > 0, 1, 0)
    p1 = np.sum(sign_profile) / max(1, len(sign_profile))
    p0 = 1.0 - p1
    binary_sign_entropy = float(-(p1 * math.log2(p1 + 1e-12) + p0 * math.log2(p0 + 1e-12)))

    # 9-я метрика: Прокси Бенфорда (тест аномалий распределения мантиссы)
    first_digits = [int(str(abs(x)).replace('.', '').lstrip('0')[0]) for x in prices if abs(x) > 1e-4]
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
        "Рыночная_Экология": model_name,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Среднее": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение": safe_num(std_val, 4),
        "Метрика_4_Минимум": safe_num(np.min(prices), 4),
        "Метрика_5_Максимум": safe_num(np.max(prices), 4),
        "Метрика_6_Аномалия_Переходов": safe_num(step_anomaly, 4),
        "Метрика_7_Автокорреляция_Лаг1": safe_num(ac_lag1, 4),
        "Метрика_8_Энтропия_Направлений": safe_num(binary_sign_entropy, 4),
        "Метрика_9_Прокси_Бенфорда": safe_num(benford_deviation_proxy, 6),
        "Суммарный_Объем": safe_num(np.sum(volumes), 2) # <- Агрегированная метрика по объемам
    }

# =====================================================================
# ЗАПУСК КРИПТО-КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛸 HASE v2.0-ECOLOGY: СИНТЕТИКА ОБЪЕМОВ И СПЯЩИХ РЫНКОВ")
    print("="*60)
    
    mega_dataset = []
    start_time = time.time()
    
    for m_type in MARKET_MODELS:
        print(f"🌲 Моделируем экосистему для паттерна: {m_type}...")
        for i in range(ROWS_PER_MODEL):
            row_id = f"{m_type.upper()}_ECO_{i+1}"
            
            # 1. Генерируем два связанных ряда: Цены и Объемы
            raw_prices, raw_volumes = generate_crypto_market_ecology(m_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Перемалываем метриками
            analysis = analyze_crypto_light(row_id, m_type, raw_prices, raw_volumes)
            
            # Сохраняем сырые финансовые потоки
            analysis["Сырой_Поток_Цен"] = ", ".join(map(lambda x: str(round(x, 4)), raw_prices))
            analysis["Сырой_Поток_Объемов"] = ", ".join(map(lambda x: str(round(x, 4)), raw_volumes))
            
            mega_dataset.append(analysis)
        print(f"   📊 Паттерн {m_type} успешно вшит в матрицу.")
      
  # Запись результатов в файл
  df = pd.DataFrame(mega_dataset)
  df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")print("\n" + "="*60)

  print(f"👑 ЭКОСИСТЕМА РЫНКА УСПЕШНО СГЕНЕРИРОВАНА!")
  print(f"📊 Всего сгенерировано: {len(df)} сложных эко-профилей (Цена + Объем).")
  print(f"📂 Результат сохранен в: {OUTPUT_FILE}")
  print(f"⏱️ Скорость симуляции: {round(time.time() - start_time, 2)} сек.")print("="*60)
