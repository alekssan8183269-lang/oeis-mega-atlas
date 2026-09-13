import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО КОСМИЧЕСКОГО КОНВЕЙЕРА (DARK MATTER)
# =====================================================================
SEQ_LENGTH = 115            # Длина ряда (время/глубина пролета частицы через ксенон)
ROWS_PER_PARTICLE = 35      # Количество уникальных сигналов на каждый тип материи
OUTPUT_FILE = "dark_matter_signals_2026_dataset.csv"

# Гипотетические модели темной материи по препринтам сентября 2026 года
PARTICLE_TYPES = ["Heavy_WIMP_Vortex", "Supersymmetric_Higgsino", "Axion_Field_Fluctuation", "Sterile_Neutrino_Trace"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ФИЗИЧЕСКИЙ СИНТЕТИЗАТОР ВСПЫШЕК ТЕМНОЙ МАТЕРИИ (LUX-ZEPLIN ИМИТАТОР)
# =====================================================================
def generate_dark_matter_signal(particle_type, length, row_idx):
    """Симулирует выделение энергии квантовых вспышек в жидком ксеноне"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 97)
    
    time_series = []
    t_steps = np.linspace(0, 10, length)
    
    # Индивидуальные параметры масс и сечений взаимодействия по препринтам 2026
    coupling_constant = np.random.uniform(0.8, 1.2)
    
    for t in t_steps:
        if particle_type == "Heavy_WIMP_Vortex":
            # Классический тяжелый WIMP: редкий, одиночный, но мощнейший пик отдачи ядра
            # Физика Гауссова всплеска кинетического удара
            base_signal = 15.0 * math.exp(-((t - 5.0)**2) / 0.5) * coupling_constant
            # Добавляем мелкие затухающие эхо-отскоки атомов ксенона
            base_signal += 2.0 * math.exp(-t/3.0)
            
        elif particle_type == "Supersymmetric_Higgsino":
            # То самое Хиггсино из моделей суперсимметрии: пик тяжелый, 
            # но сопровождается биполярной квантовой осцилляцией за счет смешивания фаз
            base_signal = 12.0 * math.exp(-((t - 4.5)**2) / 0.8) * math.cos(3 * t) * coupling_constant
            base_signal = abs(base_signal) + 3.0 * math.sin(t * 0.5)**2
            
        elif particle_type == "Axion_Field_Fluctuation":
            # Аксионное поле: сверхлегкие частицы ведут себя как фоновая когерентная волна.
            # Вместо пиков — бесконечное фрактальное мерцание с интерференцией Примакова
            base_signal = (math.sin(2 * t) + 0.5 * math.cos(7 * t + row_idx) + 1.2) * 4.0 * coupling_constant
            
        else: # Sterile_Neutrino_Trace
            # Стерильное нейтрино: каскадный распад с экспоненциальным затуханием 
            # и резким фронтом в начале пролета через детектор
            base_signal = 18.0 * math.exp(-t / 1.5) * (1.0 - math.exp(-t * 4)) * coupling_constant

        time_series.append(base_signal)
        
    # ВПРИСК КВАНТОВОГО ШУМА (1%): Симулируем те самые фоновые помехи кабелей, нейтрино от Солнца
    # и искровые разряды фотодатчиков, из-за которых физики спорят о Сигмах!
    raw_array = np.array(time_series, dtype=float)
    background_noise = np.random.normal(0, 0.15, size=length) # Реалистичный фоновый шум детектора
    return np.abs(raw_array + background_noise)

# =====================================================================
# ШАГ 2: СПЕКТРОМЕТР ИИ-СИТА (РОВНО 9 ПРОБИВНЫХ МЕТРИК)
# =====================================================================
def analyze_dark_matter_light(seq_id, particle_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # Автокорреляция Лаг 1 (проверка, случайный ли это шум или системный след частицы)
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # Робастный MAD разброс (чистота сигнала от фонового ксенонового мусора)
    mad_score = float(np.median(np.abs(seq - np.median(seq))))
    
    # Крест-фактор (амплитуда вспышки к средней мощности шума — главный маркер WIMPов)
    crest_factor = float(np.max(seq) / (mean_val + 1e-12))

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    # Высший ИИ-Вердикт
    if crest_factor > 4.0 and step_anomaly > 5.0:
        verdict = "Confirmed Dark Matter Candidate Peak (5-Sigma Path)"
    elif ac_lag1 > 0.8:
        verdict = "Coherent Axion Field Wave Background"
    else:
        verdict = "Indeterminate Cryogenic Xenon Noise Fluctuation"

    return {
        "ID": f'="{seq_id}"',
        "Модель_Темной_Материи": particle_name,
        "ИИ_Квантовый_Вердикт": verdict,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Среднее_Выделение_Энергии": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение_Вспышки": safe_num(std_val, 4),
        "Метрика_4_Минимум_Энергии": safe_num(np.min(seq), 4),
        "Метрика_5_Максимум_Энергии": safe_num(np.max(seq), 4),
        "Метрика_6_Резкость_Квантового_Пика": safe_num(step_anomaly, 4),
        "Метрика_7_Когерентность_Фронта_Lag1": safe_num(ac_lag1, 4),
        "Метрика_8_Робастность_Помех_MAD": safe_num(mad_score, 4),
        "Метрика_9_Крест_Фактор_Аномалии": safe_num(crest_factor, 4)
    }

# =====================================================================
# ЗАПУСК КВАНТОВО-КОСМИЧЕСКОГО КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*75)
    print("🛸 HASE v1.0-DARK_MATTER: СИНТЕТИЗАТОР СИГНАЛОВ ХИГГСИНО И WIMP (ПРЕПРИНТЫ 2026г)")
    print("="*75)
    
    mega_dark_dataset = []
    start_time = time.time()
    
    for p_type in PARTICLE_TYPES:
        print(f"🪸 Симулируем треки в жидком ксеноне для класса: {p_type}...")
        for i in range(ROWS_PER_PARTICLE):
            row_id = f"{p_type.upper()}_TRACK_{i+1}"
            
            # 1. Генерируем квантовый профиль вспышки
            raw_seq = generate_dark_matter_signal(p_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Вычисляем физический паспорт из 9 метрик
            analysis = analyze_dark_matter_light(row_id, p_type, raw_seq)
            analysis["Сырой_Спектр_Выделения_Энергии_eV"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_dark_dataset.append(analysis)
            
        print(f"   📊 Частица {p_type} успешно смоделирована в батче.")

    # Запись в CSV-файл
    df = pd.DataFrame(mega_dark_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*75)
    print(f"👑 КВАНТОВАЯ ГЕНЕРАЦИЯ. Атлас темной материи готов.")
    print(f"📊 Всего оцифровано: {len(df)} симуляций подземных пролетов частиц.")
    print(f"📂 Финальная матрица запечатана: {OUTPUT_FILE}")
    print(f"⏱️ Время работы процессора: {round(time.time() - start_time, 2)} sek.")
    print("="*75)
