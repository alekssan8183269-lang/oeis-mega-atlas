import os
import time
import math
import numpy as np
import pandas as pd

# Скрипт симулирует прохождение когерентного света через 4 типа сложнейших пространственных фракталов:
# функцию Вейерштрасса-Мандельброта, пыль Кантора, ковер Серпинского и квантовый дифракционный хаос. 
# На выходе лазерный луч расщепляется на бесконечное количество фрактальных Bragg-пиков (иглы в иглах), 
# а наш спектрометр снимает с этого поля 8  волновых метрик.

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО ВОЛНОВОГО КОНВЕЙЕРА
# =====================================================================
SEQ_LENGTH = 120            # Разрешение экрана наблюдения (количество точек замера поля)
ROWS_PER_FRACTAL = 35       # Количество уникальных лазерных спектров на каждый фрактал
OUTPUT_FILE = "wave_fractal_diffraction_dataset.csv"

# Типы фрактальных лазерных решеток (экранов расщепления)
FRACTAL_TYPES = ["Weierstrass_Mandelbrot_Grate", "Cantor_Dust_Interference", "Sierpinski_Carpet_Diffraction", "Quantum_Wave_Chaos"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР КВАНТОВЫХ ИНТЕРФЕРЕНЦИОННЫХ КОВРОВ (СВЕТ + ФРАКТАЛЫ)
# =====================================================================
def generate_wave_fractal_diffraction(fractal_type, length, row_idx):
    """Моделирует распределение интенсивности лазерного света на экране после фрактальной решетки"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 83)
    
    # Сетка экрана наблюдения x (от -pi до pi)
    x_grid = np.linspace(-np.pi, np.pi, length)
    intensity_profile = []
    
    # Смещение фазы лазера (дефекты линзы и термо-флуктуации среды в 1%)
    phase_shift = np.random.uniform(0.0, 2 * np.pi)
    
    for x in x_grid:
        if fractal_type == "Weierstrass_Mandelbrot_Grate":
            # Истинный фрактал Вейерштрасса: непрерывен, но нигде не дифференцируем
            # Симулирует бесконечные вложенные Bragg-пики интерференции
            wave_sum = 0.0
            b = 2.5  # Масштаб фрактального сжатия частоты
            h = 0.5  # Фрактальная размерность Холдера
            for n in range(1, 8):  # 7 уровней вложенности лазерных гармоник
                wave_sum += (math.cos((b**n) * x + phase_shift)) / (b**(h * n))
            intensity = (wave_sum + 1.5) ** 2
            
        elif fractal_type == "Cantor_Dust_Interference":
            # Дифракция на прерывистой пыли Кантора (самоподобные прорези)
            wave_sum = 0.0
            for n in: # Частотные барьеры Кантора
                wave_sum += math.cos(n * x + phase_shift) * (1.0 / math.sqrt(n))
            intensity = abs(wave_sum) ** 1.5
            
        elif fractal_type == "Sierpinski_Carpet_Diffraction":
            # Проекция двумерного ковра Серпинского на одномерный экран лазера
            wave_sum = math.sin(x) * math.cos(3 * x + phase_shift)
            # Моделируем "дыры" фрактальной решетки через нелинейную модуляцию амплитуды
            for k in range(1, 5):
                wave_sum += math.sin((3**k) * x) / (2**k)
            intensity = (wave_sum + 2.0) ** 2
            
        else: # Quantum_Wave_Chaos
            # Суперпозиция случайных квантовых фаз (модель случайных матриц Брэгга)
            wave_sum = 0.0
            for _ in range(12):  # Смешиваем 12 случайных когерентных лучей
                rand_freq = np.random.uniform(1.0, 15.0)
                wave_sum += math.cos(rand_freq * x + np.random.uniform(0, 2*np.pi))
            intensity = (wave_sum / 3.46) ** 2  # Нормируем дисперсию амплитуды
            
        intensity_profile.append(intensity)
        
    # Впрыскиваем 1% классического аналогового шума запыленности воздуха в лаборатории
    raw_array = np.array(intensity_profile, dtype=float)
    noise_layer = np.random.normal(0, np.mean(raw_array) * 0.01, size=length)
    return np.abs(raw_array + noise_layer)

# =====================================================================
# ШАГ 2: ВОЛНОВОЙ СПЕКТРОМЕТР ИИ-СИТА (РОВНО 8 МЕТРИК)
# =====================================================================
def analyze_wave_light(seq_id, fractal_name, seq):
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    diffs = np.diff(seq)
    
    # 7-я метрика: Быстрая автокорреляция Лаг 1 (когерентность волны во времени/пространстве)
    if len(seq) > 1:
        x_lag, y_lag = seq[:-1] - np.mean(seq[:-1]), seq[1:] - np.mean(seq[1:])
        ac_lag1 = float(np.mean(x_lag * y_lag) / (np.std(seq[:-1]) * np.std(seq[1:]) + 1e-12))
    else: ac_lag1 = 0.0

    # 8-я метрика: Волновой показатель "остроты пиков" (Крест-фактор / Crest Factor)
    # Показывает отношение пиковой лазерной вспышки к средней мощности ковра
    crest_factor = float(np.max(seq) / (mean_val + 1e-12))

    mean_step = np.mean(np.abs(diffs)) if len(diffs) > 0 else 0.0
    step_anomaly = float(np.max(np.abs(diffs)) / (mean_step + 1e-8)) if len(diffs) > 0 else 0.0

    # Высший ИИ-Вердикт для физиков
    if crest_factor > 3.5:
        verdict = "Fractal Bragg Multi-Peak Spectrum"
    else:
        verdict = "Continuous Ergodic Interfere Pattern"

    return {
        "ID": f'="{seq_id}"',
        "Тип_Фрактальной_Решетки": fractal_name,
        "ИИ_Волновой_Вердикт": verdict,
        "Метрика_1_Длина": safe_num(n_len, 0),
        "Метрика_2_Средняя_Интенсивность_Света": safe_num(mean_val, 4),
        "Метрика_3_Станд_Отклонение_Поля": safe_num(std_val, 4),
        "Метрика_4_Минимум_Поля": safe_num(np.min(seq), 4),
        "Метрика_5_Максимум_Поля": safe_num(np.max(seq), 4),
        "Метрика_6_Градиент_Резкости_Иглы": safe_num(step_anomaly, 4),
        "Метрика_7_Когерентность_Autocorr_Lag1": safe_num(ac_lag1, 4),
        "Метрика_8_Крест_Фактор_Вспышки": safe_num(crest_factor, 4)
    }

# =====================================================================
# ЗАПУСК ВОЛНОВОГО СИНТЕТИЗАТОРА
# =====================================================================
if __name__ == "__main__":
    print("="*75)
    print("🛸 HASE v6.0-WAVES: СОЗДАНИЕ СИНТЕТИЧЕСКОЙ ЭКОСИСТЕМЫ ФРАКТАЛЬНОЙ ДИФРАКЦИИ СВЕТА")
    print("="*75)
    
    mega_wave_dataset = []
    start_time = time.time()
    
    for f_type in FRACTAL_TYPES:
        print(f"🪸 Пропускаем лазер через фрактал: {f_type}...")
        for i in range(ROWS_PER_FRACTAL):
            row_id = f"{f_type.upper()}_WAVE_{i+1}"
            
            # 1. Симулируем прохождение когерентного света сквозь фрактальный барьер
            raw_seq = generate_wave_fractal_diffraction(f_type, SEQ_LENGTH, row_idx=i)
            
            # 2. Вычисляем волновой паспорт из 8 фич
            analysis = analyze_wave_light(row_id, f_type, raw_seq)
            analysis["Сырой_Спектр_Интенсивности"] = ", ".join(map(lambda x: str(round(x, 4)), raw_seq))
            
            mega_wave_dataset.append(analysis)
            
        print(f"   📊 Решетка {f_type} успешно просчитана и оцифрована.")

    # Запись в CSV-файл
    df = pd.DataFrame(mega_wave_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*75)
    print(f"👑 Квантовые ковры интерференции лазеров готовы")
    print(f"📊 Всего оцифровано: {len(df)} уникальных лазерных фрактальных интерференций.")
    print(f"📂 Финальный файл запечатан: {OUTPUT_FILE}")
    print(f"⏱️ Время работы процессора: {round(time.time() - start_time, 2)} сек.")
    print("="*75)
