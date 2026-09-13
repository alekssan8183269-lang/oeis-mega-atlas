import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СКОРОСТНОГО КЛИМАТИЧЕСКОГО КОНВЕЙЕРА
# =====================================================================
SEQ_LENGTH = 120            # Дистанция наблюдения (например, 120 часов/дней)
ROWS_PER_SCENARIO = 35      # Количество уникальных симуляций на каждый сценарий
OUTPUT_FILE = "climate_catastrophes_atlas.csv"

# Климатические сценарии (типы аномальных катастроф)
SCENARIOS = ["Super_Typhoon_Vortex", "Arctic_Polar_Vortex_Collapse", "Blocking_Anticyclone", "Abrupt_Jet_Stream_Shift"]

def safe_num(val, ndigits=4):
    """Защита ячеек от автоформата Excel"""
    try: return f'="{round(float(val), ndigits)}"'
    except: return f'="{val}"'

# =====================================================================
# ШАГ 1: ГЕНЕРАТОР НЕЛИНЕЙНОЙ ДИНАМИКИ АТМОСФЕРНЫХ КАТАСТРОФ
# =====================================================================
def generate_climate_anomaly(scenario, length, row_idx):
    """Симулирует уравнения атмосферного хаоса с впрыском критических аномалий"""
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 73)
    
    # Стартовые параметры атмосферного подслоя (X - скорость ветра, Y - градиент температур, Z - влажность)
    x, y, z = 1.0, 1.0, 20.0
    dt = 0.01
    
    # Физические константы Лоренца, модифицированные под климатические катастрофы
    sigma = 10.0
    beta = 8.0 / 3.0
    rho = 28.0  # Точка ухода в чистый турбулентный хаос
    
    # Сдвиг параметров под конкретные погодные коллапсы
    if scenario == "Super_Typhoon_Vortex":
        rho = 35.0  # Сверхвысокая энергия вращения циклона
    elif scenario == "Arctic_Polar_Vortex_Collapse":
        sigma = 15.0  # Растяжение струйного течения и температурный шок
    elif scenario == "Blocking_Anticyclone":
        rho = 14.0  # Стагнация, застревание системы в одной мертвой петле
        
    history_vectors = []
    
    for _ in range(length * 10):  # Делаем микрошаги для интеграции
        # Уравнения гидродинамического хаоса атмосферы
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        
        x += dx + np.random.normal(0, 0.02)
        y += dy + np.random.normal(0, 0.02)
        z += dz + np.random.normal(0, 0.02)
        
        # Записываем векторы состояния
        history_vectors.append([x, y, z])
        
    # Вырезаем шаги с нужным шагом дискретизации, имитируя замеры метеостанций
    extracted = history_vectors[::10][:length]
    return np.array(extracted, dtype=float)

# =====================================================================
# ШАГ 2: ПОГОДНЫЙ СПЕКТРОМЕТР (РОВНО 17 СПЕЦИАЛИЗИРОВАННЫХ МЕТРИК)
# =====================================================================
def analyze_climate_anomaly(seq_id, scenario_name, vectors):
    """Извлекает 17 параметров направления, градиентов, силы ветра и скрытого хаоса катастрофы"""
    n_len = len(vectors)
    
    # Вытаскиваем одномерные метео-компоненты
    wind_x = vectors[:, 0]  # Компонента скорости ветра X
    temp_y = vectors[:, 1]  # Компонента градиента температур Y
    hum_z = vectors[:, 2]   # Компонента конвекции/влажности Z
    
    # 1. Скалярная сила ветра (амплитуда результирующего вектора)
    wind_velocity = np.sqrt(wind_x**2 + temp_y**2)
    mean_wind_velocity = np.mean(wind_velocity)
    max_wind_velocity = np.max(wind_velocity)
    
    # 2. Метеорологическое направление ветра в радианах (угол фазового скольжения)
    wind_direction = np.atan2(temp_y, wind_x)
    mean_wind_direction = np.mean(wind_direction)
    var_wind_direction = np.var(wind_direction) # Флуктуация направления (сдвиг ветра)
    
    # 3. Градиенты и приращения
    diff_wind = np.diff(wind_velocity)
    diff_temp = np.diff(temp_y)
    
    # Расчет базовых статистик для выходных колонок
    mean_temp = np.mean(temp_y)
    std_temp = np.std(temp_y) + 1e-8
    mean_hum = np.mean(hum_z)
    
    # Нелинейные метрики хаоса
    # Лаг-корреляция ветра (память атмосферного фронта)
    if len(wind_velocity) > 1:
        x_lag = wind_velocity[:-1] - np.mean(wind_velocity[:-1])
        y_lag = wind_velocity[1:] - np.mean(wind_velocity[1:])
        ac_wind_lag1 = float(np.mean(x_lag * y_lag) / (np.std(wind_velocity[:-1]) * np.std(wind_velocity[1:]) + 1e-12))
    else: ac_wind_lag1 = 0.0
        
    # Коэффициент бароклинной нестабильности (отношение сдвига ветра к температуре)
    baroclinic_instability_proxy = float(np.std(diff_wind) / (std_temp + 1e-12))
    
    # Аномалия градиента давления/температуры (Черный лебедь погоды)
    mean_step_temp = np.mean(np.abs(diff_temp)) if len(diff_temp) > 0 else 1e-8
    thermal_shock_ratio = float(np.max(np.abs(diff_temp)) / mean_step_temp) if len(diff_temp) > 0 else 0.0
    
    # Извилистость струйного течения (Tortuosity)
    total_trajectory_len = np.sum(np.sqrt(np.diff(wind_x)**2 + np.diff(temp_y)**2 + np.diff(hum_z)**2))
    start_end_dist = np.sqrt((wind_x[0]-wind_x[-1])**2 + (temp_y[0]-temp_y[-1])**2 + (hum_z[0]-hum_z[-1])**2)
    jet_stream_tortuosity = float(total_trajectory_len / (start_end_dist + 1e-8))

    # Робастный MAD разброс влажности (мощность грозового облака)
    humidity_mad = float(np.median(np.abs(hum_z - np.median(hum_z))))

    # ИИ-Топологический вердикт
    if jet_stream_tortuosity > 5.0 and var_wind_direction > 1.0:
        verdict = "Extreme Turbulent Cyclonic Vortex"
    elif ac_wind_lag1 > 0.85:
        verdict = "Persistent Climate Blockade"
    else:
        verdict = "High-Entropy Meteorological Chaos"

    # Пакуем ровно 17 специализированных климатических параметров
    return {
        "ID": f'="{seq_id}"',
        "Климатический_Сценарий": scenario_name,
        "ИИ_Метео_Вердикт": verdict,
        "Параметр_1_Средняя_Скорость_Ветра": safe_num(mean_wind_velocity, 3),
        "Параметр_2_Пиковый_Порыв_Ветра": safe_num(max_wind_velocity, 3),
        "Параметр_3_Среднее_Направление_Ветра": safe_num(mean_wind_direction, 4),
        "Параметр_4_Сдвиг_Направления_Ветра": safe_num(var_wind_direction, 4),
        "Параметр_5_Средняя_Температура_Фронта": safe_num(mean_temp, 2),
        "Параметр_6_Волатильность_Температур": safe_num(std_temp, 3),
        "Параметр_7_Средняя_Влажность_Конвекции": safe_num(mean_hum, 2),
        "Параметр_8_Мощность_Облачности_MAD": safe_num(humidity_mad, 4),
        "Параметр_9_Память_Погоды_Lag1": safe_num(ac_wind_lag1, 4),
        "Параметр_10_Бароклинная_Нестабильность": safe_num(baroclinic_instability_proxy, 4),
        "Параметр_11_Коэффициент_Термошока": safe_num(thermal_shock_ratio, 3),
        "Параметр_12_Извилистость_Течений": safe_num(jet_stream_tortuosity, 4),
        "Параметр_13_Длина_Климатического_Следа": safe_num(total_trajectory_len, 2),
        "Параметр_14_Асимметрия_Ветров": safe_num(float(stats.skew(wind_velocity)), 4),
        "Параметр_15_Эксцесс_Температурных_Хвостов": safe_num(float(stats.kurtosis(temp_y)), 4),
        "Параметр_16_Минимальное_Давление_Ядра": safe_num(np.min(hum_z), 2),
        "Параметр_17_Максимальный_Шаг_Ветра": safe_num(np.max(np.abs(diff_wind)), 3)
    }

# =====================================================================
# ГЛАВНЫЙ ЗАПУСК КЛИМАТИЧЕСКОГО КОНВЕЙЕРА
# =====================================================================
if __name__ == "__main__":
    print("="*75)
    print("🛸 HASE v6.0-CLIMATE: ГЕНЕРАТОР АТЛАСОВ КЛИМАТИЧЕСКИХ КАТАСТРОФ")
    print("="*75)
    
    mega_atlas = []
    start_time = time.time()
    
    for sc in SCENARIOS:
        print(f"🪸 Запуск симуляции суперкомпьютера для сценария: {sc}...")
        for i in range(ROWS_PER_SCENARIO):
            row_id = f"{sc.upper()}_SCENARIO_{i+1}"
            
            # 1. Генерируем 3D фазовую траекторию погодной катастрофы
            matrix_seq = generate_climate_anomaly(sc, SEQ_LENGTH, row_idx=i)
            
            # 2. Вычисляем метео-паспорт из 17 параметров
            analysis = analyze_climate_anomaly(row_id, sc, matrix_seq)
            
            # Записываем результирующий скалярный временной ряд силы ветра для наглядности датасета
            wind_scalar = np.sqrt(matrix_seq[:, 0]**2 + matrix_seq[:, 1]**2)
            analysis["Сырой_Ряд_Скорости_Ветра"] = ", ".join(map(lambda x: str(round(x, 4)), wind_scalar))
            
            mega_atlas.append(analysis)
            
        print(f"   📊 Сценарий {sc} успешно смоделирован и оцифрован.")

    # Сохраняем в CSV
    df = pd.DataFrame(mega_atlas)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*75)
    print(f"👑 КЛИМАТИЧЕСКИЙ АТЛАС УСПЕШНО СФОРМИРОВАН!")
    print(f"📊 Всего оцифровано: {len(df)} экстремальных погодных симуляций.")
    print(f"📂 Файл сохранен: {OUTPUT_FILE}")
    print(f"⏱️ Время работы процессора: {round(time.time() - start_time, 2)} сек.")
    print("="*75)
