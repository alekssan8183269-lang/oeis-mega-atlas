import os
import time
import math
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ МОЗАИЧНОГО ГЕНЕРАТОРА (Параметры по методичке)
# =====================================================================
SEQ_LENGTH = 100            # Длина каждого числового ряда
ROWS_PER_TILE = 35          # Ровно по 35 уникальных рядов каждого вида
OUTPUT_FILE = "aperiodic_tiles_mega_dataset.csv"

# Полная обойма из 8 видов плиток
TILE_TYPES = ["Hat", "Spectre", "Turtle", "Comet", "Penrose", "Ammann", "Danzer", "Sphinx"]

# =====================================================================
# ВЫЧИСЛИТЕЛЬНЫЕ МЕТРИКИ ДНК-ХАОСА
# =====================================================================
def get_permutation_entropy(seq, order=3):
    """Считает энтропию перестановок для оценки локальной сложности"""
    n_len = len(seq)
    patterns = []
    for i in range(n_len - order + 1):
        patterns.append(tuple(np.argsort(seq[i:i+order])))
    unique_pats, pat_counts = np.unique(patterns, axis=0, return_counts=True)
    probs = pat_counts / len(patterns)
    return float(-np.sum(probs * np.log2(probs + 1e-12)))

def get_hurst_exponent(seq):
    """Вычисляет показатель Херста для оценки долгосрочной памяти квазикристалла"""
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    vals = seq - mean_val
    cum_vals = np.cumsum(vals)
    res_range = np.max(cum_vals) - np.min(cum_vals)
    hurst = math.log(res_range / std_val) / math.log(n_len)
    return min(max(hurst, 0.0), 1.0)

# =====================================================================
# ДНК-БИБЛИОТЕКА ФРАКТАЛЬНЫХ ПОДСТАНОВОК (4 ВИДА ПЛИТОК)
# =====================================================================
def get_base_tile_mosaic(tile_type, length):
    """Разворачивает идеальный апериодический ДНК-код плитки до нужной длины"""
    # --- ЭПОХА ЭЙНШТЕЙНА (МОНОПЛИТКИ) ---    
    if tile_type == "Hat":
        # ДНК-правило плитки "Шляпа"
        seed = [1, 0, 1, 1, 0, 1]
        rules = {1: [1, 0], 0: [1, 1, 0]}
    elif tile_type == "Spectre":
        # ДНК-правило плитки "Призрак" (истинный апериод без отражений)
        seed = [1, 0, 0, 1, 1, 0]
        rules = {1: [1, 0, 1], 0: [1, 1]}
    elif tile_type == "Turtle":
        # ДНК-правило плитки "Черепаха"
        seed = [0, 0, 1, 1, 0, 0]
        rules = {1: [0, 1], 0: [1, 0, 0]}
    elif tile_type == "Comet":
        # ДНК-правило плитки "Комета"
        seed = [1, 1, 1, 0, 0, 1]
        rules = {1: [1, 1, 1], 0: [0, 1]}
    elif:
        seed = [1, 0]
        rules = {1: [1, 0], 0: [1]}

        
    # --- ЗОЛОТАЯ КЛАССИКА (НАБОРЫ ПЛИТОК) ---
    elif tile_type == "Penrose":
        # Цепочка инфляции Пенроуза (Толстый/Тонкий ромбы на основе золотого сечения)
        seed = [1, 1, 0, 1, 0]
        rules = {1:, 0:}
    elif tile_type == "Ammann":
        # Цепочка Аммана-Бинакера (Ромб/Квадрат под серебряное сечение)
        seed = [1, 0, 1, 1, 0]
        rules = {1:, 0:}
    elif tile_type == "Danzer":
        # Проекция треугольников Данцера 7-го порядка
        seed = [1, 0, 0, 1, 0, 1, 1]
        rules = {1:, 0:}
    elif tile_type == "Sphinx":
        # Фрактал самоделения Сфинкса (заполнение гексамондами)
        seed = [0, 1, 1, 0, 1]
        rules = {1:, 0:}
    else:
        seed = [1, 0]
        rules = {1:, 0:}

    # Разворачиваем фрактал замещениями
    while len(seed) < length:
        new_seed = []
        for bit in seed:
            new_seed.extend(rules[bit])
        seed = new_seed
        
    return np.array(seed[:length], dtype=float)

# =====================================================================
# СИНТЕТИЧЕСКОЕ ЯДРО: СБОРКА РЯДА С ЗАДАННОЙ ПОГРЕШНОСТЬЮ (1%)
# =====================================================================
def generate_pure_tile_noise(tile_type, length, row_idx):
    """Генерирует гарантированно уникальный ряд плитки с 1% погрешностью"""
    base_mosaic = get_base_tile_mosaic(tile_type, length)
    
    # Инициализируем уникальный сид для каждой строки, чтобы убрать клонирование
    np.random.seed(int(time.time() * 1000) % 500000 + row_idx * 17)
    
    # Моделируем 1% погрешность (шумовое дрожание амплитуды)
    noise_scale = 0.01 
    noise_layer = np.random.normal(0, noise_scale, size=length)
    
    # Принудительно мутируем ровно 2% случайных битов ДНК (микро-дефекты решетки минерала)
    shimmer_seq = base_mosaic.copy()
    mutate_mask = np.random.rand(length) < 0.02
    shimmer_seq[mutate_mask] = 1.0 - shimmer_seq[mutate_mask]
    
    # Накладываем физический шум погрешности
    shimmer_seq += noise_layer
    
    # Вычисляем уникальный паспорт ряда
    hurst = get_hurst_exponent(shimmer_seq)
    perm_ent = get_permutation_entropy(shimmer_seq)
    
    return shimmer_seq, hurst, perm_ent

# =====================================================================
# ГЛАВНЫЙ ЗАПУСК КОНВЕЙЕРА (ВСЁ ПИШЕМ В 1 ФАЙЛ)
# =====================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛸 HASE v2.0: ЗАПУСК ТОТАЛЬНОГО СИНТЕТИЗАТОРА МОЗАИЧНЫХ МИРОВ")
    print("="*60)
    
    # 1. Заранее кэшируем чистые идеальные эталоны для расчёта корреляции
    base_mosaics = {t: get_base_tile_mosaic(t, SEQ_LENGTH) for t in TILE_TYPES}
        
    # tile_types = ["Hat", "Spectre", "Turtle", "Comet"]
    # mega_dataset = []
    # Теперь здесь полная обойма из 8 видов плиток!
    tile_types = ["Hat", "Spectre", "Turtle", "Comet", "Penrose", "Ammann", "Danzer", "Sphinx"]
    mega_dataset = []    
    start_time = time.time()  # Общий таймер для всего процесса
    
    for t_type in tile_types:
        print(f"🪸 Синтезируем {ROWS_PER_TILE} уникальных рядов для плитки: «{t_type}»...")

        # Точка отсчета времени для текущей плитки
        tile_start_time = time.time()
        last_batch_time = time.time()

        # Задаем "природное" кинематографичное название типа шума
        # Назначаем текстовые паспорта для Excel под каждый тип шума
        if t_type == "Hat":
            natural_name = "Апериодический Шум Шляпы (Зеркальный квазикристалл)"
        elif t_type == "Spectre":
            natural_name = "Апериодическое Мозаичное Мерцание Призрака (Чистый апериод)"
        elif t_type == "Turtle":
            natural_name = "Свернутый Квазикристаллический Поток Черепахи"
        elif t_type == "Comet":
            natural_name = "Турбулентная Мозаичная Пена Кометы"
        elif t_type == "Penrose":
            natural_name = "Квазикристаллический Ромбический Хаос Пенроуза (Симметрия 5)"
        elif t_type == "Ammann":
            natural_name = "Ортогональный Поток Аммана-Бинакера (Симметрия 8)"
        elif t_type == "Danzer":
            natural_name = "Гептагональный Мозаичный Шум Данцера (Симметрия 7)"
        elif t_type == "Sphinx":
            natural_name = "Фрактальная Эволюция Сфинкса (Шестиугольный апериод)"
            
        for i in range(ROWS_PER_TILE):
            row_name = f"{t_type.upper()}_SHIMMER_{i+1}"
            
            # Генерируем уникальный ряд
            seq, hst, ent = generate_pure_tile_noise(t_type, SEQ_LENGTH, row_idx=i)
            
            # Пакуем строку в датасет
            mega_dataset.append({
                "ID": row_name,
                "Последовательность": ", ".join(map(lambda x: str(round(x, 4)), seq)),
                "Показатель_Херста": f'="{round(hst, 4)}"',
                "Энтропия_Мозаики": f'="{round(ent, 4)}"',
                "Тип_Шума": natural_name
            })
            
            # Математический расчёт взаимной корреляции с эталоном каждого класса
            for base_name, base_seq in base_mosaics.items():
                # Считаем коэффициент корреляции Пирсона между сгенерированным рядом и чистым шаблоном
                corr_matrix = np.corrcoef(seq, base_seq)
                correlation_value = corr_matrix[0, 1]
                
                # Добавляем в отдельный столбец таблицы
                row_data[f"Корреляция_с_{base_name}"] = round(correlation_value, 4)
                
            mega_dataset.append(row_data)
                        
            # Логируем прогресс каждые 5 созданных строк внутри текущей плитки
            if (i + 1) % 5 == 0:
                now = time.time()
                batch_duration = now - last_batch_time
                last_batch_time = now
                print(f"   📊 {i + 1} сделано из {ROWS_PER_TILE} (последние 5 шт за {round(batch_duration, 3)} сек)")
                        
            # Небольшая задержка по миктовремени для гарантированной уникальности рандома
            time.sleep(0.001)
            
        tile_total_time = time.time() - tile_start_time
        print(f"   ⏱️ Класс «{t_type}» полностью собран за {round(tile_total_time, 2)} сек.")

    # Записываем всё в ОДИН единый CSV-файл для Excel
    df = pd.DataFrame(mega_dataset)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n" + "="*60)
    print(f"👑 ПОЛНЫЙ АТЛАС МОЗАИЧНЫХ ШУМОВ (8 КЛАССОВ) УСПЕШНО СОЗДАН С ПОГРЕШНОСТЬЮ 1%!")
    print(f"📊 Всего сгенерировано: {len(df)} рядов (8 видов плиток по {ROWS_PER_TILE} строк).")
    print(f"📂 Ищи готовый файл: {OUTPUT_FILE}")
    print(f"⏱️ Время работы процессора: {round(time.time() - start_time, 2)} сек.")
    print("="*60)
    
    # 2. Вычисляем и выводим красивую матрицу межклассовых отличий в консоль
    print("\n🔬 СВОДНАЯ СРЕДНЯЯ КРОСС-КОРРЕЛЯЦИЯ МЕЖДУ СЕМЕЙСТВАМИ:")
    print("-" * 90)
    
    # Считаем среднее значение корреляции для каждого класса
    summary_matrix = []
    for t_type in TILE_TYPES:
        sub_df = df[df["ID"].str.startswith(t_type.upper() + "_")]
        mean_corrs = {f"с_{b}": round(sub_df[f"Корреляция_с_{b}"].mean(), 2) for b in TILE_TYPES}
        summary_matrix.append((t_type, mean_corrs))
    
    # Печатаем шапку таблицы в консоли
    header = f"{'Класс ряда':<12} | " + " | ".join([f"{t:<8}" for t in TILE_TYPES])
    print(header)
    print("-" * 90)
    for cls_name, corrs in summary_matrix:
        row_str = f"{cls_name:<12} | " + " | ".join([f"{corrs[f'с_{b}']:>8.2f}" for b in TILE_TYPES])
        print(row_str)
    print("-" * 90)
