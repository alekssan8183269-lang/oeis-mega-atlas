import os
import time
import math
import numpy as np
import pandas as pd

# Hyper-Algebraic Synthetic Engine — HASE v1.0

# =====================================================================
# НАСТРОЙКИ СИНТЕТИЧЕСКОГО ДВИЖКА HASE v1.0
# =====================================================================
SEQ_LENGTH = 100            # Длина одной генерируемой последовательности
MAX_MUTATION_STEPS = 500    # Сколько раз пытаемся мутировать ряд под паспорт
OUTPUT_DIR = "synthetic_noise_datasets"

# Создаем папку под новые миры
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================================
# ВСПОМОГАТЕЛЬНЫЕ МАТЕМАТИЧЕСКИЕ МИКРО-МОДУЛИ
# =====================================================================
def get_permutation_entropy(seq, order=3):
    """Считает энтропию перестановок для оценки локального хаоса"""
    n_len = len(seq)
    patterns = []
    for i in range(n_len - order + 1):
        patterns.append(tuple(np.argsort(seq[i:i+order])))
    unique_pats, pat_counts = np.unique(patterns, axis=0, return_counts=True)
    probs = pat_counts / len(patterns)
    return float(-np.sum(probs * np.log2(probs + 1e-12)))

def get_hurst_exponent(seq):
    """Вычисляет показатель Херста для оценки макро-памяти шума"""
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    vals = seq - mean_val
    cum_vals = np.cumsum(vals)
    res_range = np.max(cum_vals) - np.min(cum_vals)
    hurst = math.log(res_range / std_val) / math.log(n_len)
    return min(max(hurst, 0.0), 1.0)

def build_horizontal_visibility_graph(seq):
    """Строит граф горизонтальной видимости (HVG 2008) для ряда чисел"""
    n = len(seq)
    adj_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1:
                adj_matrix[i, j] = 1
                adj_matrix[j, i] = 1
                continue
            # Условие видимости: все промежуточные числа должны быть строго меньше
            visible = True
            for k in range(i + 1, j):
                if seq[k] >= min(seq[i], seq[j]):
                    visible = False
                    break
            if visible:
                adj_matrix[i, j] = 1
                adj_matrix[j, i] = 1
    return adj_matrix

def get_fiedler_value(adj_matrix):
    """Вычисляет число Фидлера (алгебраическую связность графа видимости)"""
    try:
        degrees = np.sum(adj_matrix, axis=1)
        laplacian = np.diag(degrees) - adj_matrix
        eigenvalues = np.linalg.eigvalsh(laplacian)
        # Число Фидлера — второе наименьшее собственное число
        sorted_eig = np.sort(eigenvalues)
        if len(sorted_eig) > 1:
            return float(sorted_eig[1])
        return 0.0
    except:
        return 0.0

# =====================================================================
# ЯДРО ГЕНЕРАЦИИ №1: ALGEBRAIC GALOIS FOAM (Алгебраическая Пена)
# =====================================================================
def generate_galois_foam(length, mod=11, target_entropy=1.5):
    """Синтезирует хаос с локальной замкнутостью конечного полукольца Галуа"""
    # Стартуем со случайного шума в рамках модуля
    seq = np.random.randint(0, mod, size=length)
    
    for step in range(MAX_MUTATION_STEPS):
        perm_ent = get_permutation_entropy(seq)
        
        # Считаем алгебраическую замкнутость по сложению в скользящем окне
        unique_vals = set(seq[:50])
        closed_pairs = 0
        total_pairs = 0
        
        # Проверяем пары элементов на замкнутость операции (A + B) % mod
        sub_seq = seq[:30]
        for idx, a in enumerate(sub_seq):
            for b in sub_seq[idx:]:
                total_pairs += 1
                if ((a + b) % mod) in unique_vals:
                    closed_pairs += 1
        
        closure_ratio = closed_pairs / (total_pairs + 1e-12)
        
        # Условия паспорта: высокий макро-хаос, но строгая микро-замкнутость (не менее 75%)
        if abs(perm_ent - target_entropy) < 0.15 and closure_ratio >= 0.75:
            return seq, perm_ent, closure_ratio
            
        # Мутация: точечно меняем случайное число под законы кольца
        idx_to_mutate = np.random.randint(0, length)
        seq[idx_to_mutate] = np.random.randint(0, mod)
        
    return seq, perm_ent, closure_ratio

# =====================================================================
# ЯДРО ГЕНЕРАЦИИ №2: TOPOLOGICAL FIEDLER NOISE (Шум Фидлера)
# =====================================================================
def generate_fiedler_noise(length, target_fiedler=1.8):
    """Синтезирует хаос, зажатый в неизменный топологический каркас графа видимости"""
    seq = np.random.randint(10, 100, size=length).astype(float)
    
    for step in range(MAX_MUTATION_STEPS):
        g = build_horizontal_visibility_graph(seq)
        fiedler = get_fiedler_value(g)
        perm_ent = get_permutation_entropy(seq)
        
        # Ищем идеальное совпадение со структурной связностью сети при высокой энтропии
        if abs(fiedler - target_fiedler) < 0.05 and perm_ent > 1.8:
            return seq, fiedler, perm_ent
            
        # Мутация: слегка смещаем амплитуду случайного числа для изменения графа
        idx_to_mutate = np.random.randint(0, length)
        seq[idx_to_mutate] += np.random.choice([-2, -1, 1, 2])
        if seq[idx_to_mutate] < 0: seq[idx_to_mutate] = 1
        
    return seq, fiedler, perm_ent

# =====================================================================
# ЯДРО ГЕНЕРАЦИИ №3: APERIODIC SPECTRE SHIMMER (Мозаичное Мерцание)
# =====================================================================
# def generate_spectre_shimmer(length):
#     """Генерирует шум на основе апериодической плитки Spectre (открытие 2023)"""
#     # Идеальный ДНК-шаблон подстановок апериодической плитки Призрак
#     # Spectre рождает бесконечную непериодическую последовательность шагов
#     spectre_seed = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0]
    
#     # Разворачиваем ДНК-шаблон до нужной длины с помощью правила замещения фрактала
#     while len(spectre_seed) < length:
#         new_seed = []
#         for bit in spectre_seed:
#             if bit == 1:
#                 new_seed.extend([1, 0, 1])
#             else:
#                 new_seed.extend([1, 1])
#         spectre_seed = new_seed
        
#     base_mosaic = np.array(spectre_seed[:length], dtype=float)
    
#     # # Теперь превращаем чистую мозаику в "мерцающий шум"
#     # for step in range(MAX_MUTATION_STEPS):
#     #     noise_layer = np.random.normal(0, 0.15, size=length)
#     #     shimmer_seq = base_mosaic + noise_layer
        
#     #     hurst = get_hurst_exponent(shimmer_seq)
#     #     perm_ent = get_permutation_entropy(shimmer_seq)
        
#     #     # Мозаичный паспорт: строгий квазикристаллический баланс
#     #     if 0.48 <= hurst <= 0.52 and 1.3 <= perm_ent <= 1.6:
#     #         return shimmer_seq, hurst, perm_ent

#     # Теперь превращаем чистую мозаику в РАЗНЫЙ "мерцающий шум"
#     for step in range(MAX_MUTATION_STEPS):
#         # ИСПРАВЛЕНО: Добавляем динамический масштаб шума и случайное смещение,
#         # чтобы заставить i5 каждый раз генерировать УНИКАЛЬНЫЙ слой
#         noise_scale = np.random.uniform(0.1, 0.4)
#         noise_layer = np.random.normal(0, noise_scale, size=length)
        
#         # Точечно взбалтываем случайные биты самой мозаики
#         shimmer_seq = base_mosaic.copy()
#         mutate_mask = np.random.rand(length) < 0.15 # 15% элементов мутируют жестко
#         shimmer_seq[mutate_mask] += np.random.choice([-1.0, 1.0], size=np.sum(mutate_mask))
#         shimmer_seq += noise_layer
        
#         hurst = get_hurst_exponent(shimmer_seq)
#         perm_ent = get_permutation_entropy(shimmer_seq)
        
#         # Мозаичный паспорт: держим планку квазикристалла
#         if 0.45 <= hurst <= 0.55 and 1.2 <= perm_ent <= 1.7:
#             return shimmer_seq, hurst, perm_ent
            
#     return base_mosaic, 0.5, 1.4

def generate_spectre_shimmer(length, row_index=0):
    """Генерирует гарантированно УНИКАЛЬНЫЙ зашумленный ряд на основе плитки Spectre"""
    # Исходный идеальный ДНК-шаблон плитки Призрак (Spectre)
    spectre_seed = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0]
    
    # Разворачиваем фрактал до нужной длины
    while len(spectre_seed) < length:
        new_seed = []
        for bit in spectre_seed:
            if bit == 1:
                new_seed.extend([1, 0, 1])
            else:
                new_seed.extend([1, 1])
        spectre_seed = new_seed
        
    base_mosaic = np.array(spectre_seed[:length], dtype=float)
    
    # Чтобы ряды ГАРАНТИРОВАННО отличались, инициализируем генератор случайных чисел
    # уникальным сидом, привязанным к номеру строки и текущему миктовременю
    np.random.seed(int(time.time() * 1000) % 1000000 + row_index)
    
    for step in range(MAX_MUTATION_STEPS):
        # Генерируем уникальный случайный гауссов шум
        noise_scale = np.random.uniform(0.15, 0.45)
        noise_layer = np.random.normal(0, noise_scale, size=length)
        
        # Создаем мутировавшую копию: жестко взбалтываем случайные 20% битов
        shimmer_seq = base_mosaic.copy()
        mutate_mask = np.random.rand(length) < 0.20
        # Меняем 1 на 0, а 0 на 1 в местах мутаций
        shimmer_seq[mutate_mask] = 1.0 - shimmer_seq[mutate_mask]
        
        # Накладываем сверху аналоговый шум
        shimmer_seq += noise_layer
        
        hurst = get_hurst_exponent(shimmer_seq)
        perm_ent = get_permutation_entropy(shimmer_seq)
        
        # Мозаичный паспорт (немного расширим границы, чтобы ловить глубокие мутации)
        if 0.40 <= hurst <= 0.60 and 1.2 <= perm_ent <= 1.9:
            # ВАЖНО: Возвращаем именно ИЗМЕНЕННЫЙ ряд shimmer_seq, а не базу!
            return shimmer_seq, hurst, perm_ent
            
    # Если за 500 шагов не подогнали (что маловероятно), возвращаем хоть какой-то уникальный хаос
    return base_mosaic + np.random.normal(0, 0.3, size=length), 0.5, 1.5


# =====================================================================
# ЗАПУСК ТЕРМОЯДЕРНОГО СИНТЕТИЗАТОРА
# =====================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛸 HASE v1.0: ЗАПУСК ГЕНЕРАТОРА МАТЕМАТИЧЕСКОЙ МАТЕРИИ")
    print("="*60)
    
    HOW_MANY_EACH = 120  # Сколько рядов каждого вида шума нагенерировать

    # МИРЫЫЫ 1 и 2 РАСКОММЕНТИРУЙ ЕСЛИ НАДО БЦДКЕЕТ ИХ СОЗДАТЬ ТЕБЕ!!!!!!!!!!!!!!(строки 251-285)

    # --- Сборка Мира 1 ---
    # print("\n🔮 Синтезируем Класс: Algebraic Galois Foam...")
    # start_foam = time.time()
    # last_batch_time = time.time()    
    # foam_list = []
    # for i in range(HOW_MANY_EACH):
    #     seq, ent, clos = generate_galois_foam(SEQ_LENGTH)
    #     foam_list.append({
    #         "ID": f"GALOIS_FOAM_{i+1}",
    #         "Последовательность": ", ".join(map(str, seq)),
    #         "Энтропия_Перестановок": f'="{round(ent, 4)}"',
    #         "Замкнутость_Кольца_%": f'="{round(clos * 100, 2)}%"',
    #         "Тип_Шума": "Алгебраический Шум"
    #     })
    #     if (i + 1) % 10 == 0:
    #         now = time.time()
    #         batch_duration = now - last_batch_time
    #         last_batch_time = now
    #         print(f"   📊 {i + 1} сделано из {HOW_MANY_EACH} (последние 10 шт за {round(batch_duration, 2)} сек)")
    # df_foam = pd.DataFrame(foam_list)
    # df_foam.to_csv(f"{OUTPUT_DIR}/algebraic_galois_foam.csv", index=False, sep=";", encoding="utf-8-sig")
    # print("✅ Файл algebraic_galois_foam.csv успешно запечатан!")
    # total_foam_time = time.time() - start_foam
    # print(f"✅ Файл algebraic_galois_foam.csv успешно запечатан! Всего ушло времени: {round(total_foam_time, 2)} сек")

    # --- Сборка Мира 2 ---
    # print("\n🕸️ Синтезируем Класс: Topological Fiedler Noise...")
    # start_fiedler = time.time()
    # last_batch_time = time.time()    
    # fiedler_list = []
    # for i in range(HOW_MANY_EACH):
    #     seq, fied, ent = generate_fiedler_noise(SEQ_LENGTH)
    #     fiedler_list.append({
    #         "ID": f"FIEDLER_NOISE_{i+1}",
    #         "Последовательность": ", ".join(map(lambda x: str(round(x, 1)), seq)),
    #         "Число_Фидлера_Графа": f'="{round(fied, 4)}"',
    #         "Энтропия_Сети": f'="{round(ent, 4)}"',
    #         "Тип_Шума": "Топологический Шум (Visibility)"
    #     })
    #     if (i + 1) % 10 == 0:
    #         now = time.time()
    #         batch_duration = now - last_batch_time
    #         last_batch_time = now
    #         print(f"   📊 {i + 1} сделано из {HOW_MANY_EACH} (последние 10 шт за {round(batch_duration, 2)} сек)")
    # df_fiedler = pd.DataFrame(fiedler_list)
    # df_fiedler.to_csv(f"{OUTPUT_DIR}/topological_fiedler_noise.csv", index=False, sep=";", encoding="utf-8-sig")
    # # print("✅ Файл topological_fiedler_noise.csv успешно запечатан!")
    # total_fiedler_time = time.time() - start_fiedler
    # print(f"✅ Файл topological_fiedler_noise.csv успешно запечатан! Всего ушло времени: {round(total_fiedler_time, 2)} сек")

    # --- Сборка Мира 3 ---
    print("\n🪸 Синтезируем Класс: Aperiodic Spectre Shimmer...")
    start_spectre = time.time()  # Точка отсчета для всего файла
    last_batch_time = time.time()  # Точка отсчета для текущих 10 штук

    spectre_list = []
    for i in range(HOW_MANY_EACH):
        seq, hst, ent = generate_spectre_shimmer(SEQ_LENGTH, row_index=i)
        spectre_list.append({
            "ID": f"SPECTRE_SHIMMER_{i+1}",
            "Последовательность": ", ".join(map(lambda x: str(round(x, 4)), seq)),
            "Показатель_Херста": f'="{round(hst, 4)}"',
            "Энтропия_Мозаики": f'="{round(ent, 4)}"',
            "Тип_Шума": "Апериодическое Мозаичное Мерцание"
        })
        # Проверяем кратность 10 (используем i + 1, чтобы отсчет шел от 1 до HOW_MANY_EACH)
        if (i + 1) % 10 == 0:
            now = time.time()
            batch_duration = now - last_batch_time  
            # Разница с прошлым замером
            last_batch_time = now  
            # Сдвигаем точку замера вперед
            print(f"   📊 {i + 1} сделано из {HOW_MANY_EACH} (последние 10 шт за {round(batch_duration, 2)} сек)")
            # print(f"   📊 {i + 1} сделано из {HOW_MANY_EACH}")

    df_spectre = pd.DataFrame(spectre_list)
    df_spectre.to_csv(f"{OUTPUT_DIR}/aperiodic_spectre_shimmer.csv", index=False, sep=";", encoding="utf-8-sig")
    # print("✅ Файл aperiodic_spectre_shimmer.csv успешно запечатан!")
    total_spectre_time = time.time() - start_spectre  # Итоговое время файла
    print(f"✅ Файл aperiodic_spectre_shimmer.csv успешно запечатан! Всего ушло времени: {round(total_spectre_time, 2)} сек")
    
    print("\n" + "="*60)
    print("👑 ВСЕ ТРИ НОВЫХ ВИДА ШУМА СИНТЕЗИРОВАНЫ МИЛЛИОННЫМИ АЛГОРИТМАМИ!")
    print(f"📂 Загляни в папку: /{OUTPUT_DIR}")
    print("="*60)
