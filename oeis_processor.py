import os
import time
import math
import gzip
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ КОНВЕЙЕРА (Безопасно для i5 и 8GB ОЗУ)
# =====================================================================
BATCH_SIZE = 20           # Обрабатываем строго по 20 последовательностей за раз
EMBEDDING_DIM = 3         # Размерность пространства (3D-векторы: X, Y, Z)
INPUT_STRIPPED = "stripped.gz" # Файл с числами
INPUT_NAMES = "names.gz"       # Файл с названиями последовательностей
OUTPUT_FILE = "oeis_atlas_results.csv"

# Лимит на этот запуск (поставьте 1000 для теста, или 360000 для всей базы!)
LIMIT_SEQUENCES = 1000  

# Вспомогательная безопасная функция корреляции (вместо капризного np.corrcoef)
def safe_correlation(x, y):
    if len(x) < 2 or len(y) < 2:
        return 0.0
    std_x, std_y = np.std(x), np.std(y)
    if std_x < 1e-8 or std_y < 1e-8:
        return 0.0
    # Классическая формула Пирсона: ковариация / (std_x * std_y)
    cov = np.mean((x - np.mean(x)) * (y - np.mean(y)))
    corr = float(cov / (std_x * std_y))
    return 0.0 if np.isnan(corr) else corr

# =====================================================================
# ФУНКЦИЯ МАКСИМАЛЬНОГО МАТЕМАТИЧЕСКОГО АНАЛИЗА РЯДА (15 МЕТРИК)
# =====================================================================
def analyze_sequence(seq_id, seq_name, raw_sequence):
    seq = np.array(raw_sequence, dtype=float)
    seq = seq[np.isfinite(seq)]
    
    if len(seq) < EMBEDDING_DIM + 10: 
        return {"ID": seq_id, "Название": seq_name, "Вердикт": "Слишком короткий ряд", "Status": "Skip"}

    # Выводим дебаг-принт в консоль, чтобы видеть прогресс
    print(f"🔎 Анализируем: {seq_id} | Длина: {len(seq)} чисел | Имя: {seq_name[:45]}...")

    # Построение 3D-траектории (Теорема Такенса)
    num_vectors = len(seq) - EMBEDDING_DIM + 1
    vectors = np.zeros((num_vectors, EMBEDDING_DIM))
    for i in range(EMBEDDING_DIM):
        vectors[:, i] = seq[i : i + num_vectors]

    diffs = np.diff(seq)
    n_len = len(seq)

    # 1. Энтропия Шеннона
    _, counts = np.unique(seq, return_counts=True)
    probs = counts / n_len
    shannon_ent = float(-np.sum(probs * np.log2(probs + 1e-12)))

    # 2. Энтропия перестановок
    patterns = []
    for i in range(n_len - 2):
        chunk = seq[i:i+3]
        patterns.append(tuple(np.argsort(chunk)))
    unique_pats, pat_counts = np.unique(patterns, axis=0, return_counts=True)
    pat_probs = pat_counts / len(patterns)
    perm_ent = float(-np.sum(pat_probs * np.log2(pat_probs + 1e-12)))

    # 3. Фрактальная размерность GP (Приближенная)
    try:
        sub_vecs = vectors[:50] 
        dists = np.linalg.norm(sub_vecs[:, None, :] - sub_vecs[None, :, :], axis=-1)
        flat_dists = dists[np.triu_indices_from(dists, k=1)]
        r = np.median(flat_dists) * 0.5
        corr_sum = np.sum(flat_dists < r) / (len(flat_dists) + 1e-8)
        corr_dim = float(np.log(corr_sum + 1e-12) / np.log(r + 1e-12))
        corr_dim = min(max(corr_dim, 0.0), 3.0)
    except:
        corr_dim = 1.0

    # 4. Асимметрия (Skewness)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8
    skewness = float(np.mean((seq - mean_val) ** 3) / (std_val ** 3))

    # 5. Эксцесс (Kurtosis)
    kurtosis = float(np.mean((seq - mean_val) ** 4) / (std_val ** 4)) - 3.0

    # 6. Автокорреляция с лагом 1 (Через нашу безопасную функцию)
    ac_lag1 = safe_correlation(seq[:-1], seq[1:])

    # 7. Показатель Херста
    try:
        vals = seq - mean_val
        cum_vals = np.cumsum(vals)
        res_range = np.max(cum_vals) - np.min(cum_vals)
        hurst = math.log(res_range / (std_val + 1e-8)) / math.log(n_len)
        hurst = min(max(hurst, 0.0), 1.0)
    except:
        hurst = 0.5

    # 8. Плотность/Радиус облака точек
    center = np.mean(vectors, axis=0)
    cloud_radius = float(np.mean(np.linalg.norm(vectors - center, axis=1)))

    # 9. Коэффициент структурного сдвига
    mean_step = np.mean(np.abs(diffs))
    step_anomaly_ratio = float(np.max(np.abs(diffs)) / (mean_step + 1e-8))

    # 10, 11, 12. Тензорное PCA-сжатие осей
    try:
        _, S, _ = np.linalg.svd(vectors - center, full_matrices=False)
        pca_x, pca_y, pca_z = float(S[0]/np.sum(S)), float(S[1]/np.sum(S)), float(S[2]/np.sum(S))
    except:
        pca_x, pca_y, pca_z = 0.33, 0.33, 0.33

    # 13. Сила закрутки Ротора
    cross_products = np.cross(vectors[:-1], vectors[1:])
    vector_rot_force = float(np.mean(np.linalg.norm(cross_products, axis=1)))

    # 14. Сквозные дыры
    start_end_dist = np.linalg.norm(vectors[0] - vectors[-1])
    has_hollow_holes = 1.0 / (start_end_dist + 1e-5)

    # 15. Ветвление / Кораллизация (Тоже через безопасную функцию)
    branch_ratio = safe_correlation(diffs[:-1], diffs[1:])

    try:
        fft_vals = np.abs(np.fft.fft(seq))
        main_freq = float(np.argmax(fft_vals[1:len(fft_vals)//2]) + 1)
    except:
        main_freq = 0.0

    # Умный Вердикт компьютера
    if perm_ent < 1.0 and ac_lag1 > 0.8:
        verdict = "Строгий кристаллический тренд"
    elif shannon_ent > 4.0 and corr_dim > 2.2:
        verdict = "Многомерный фрактальный Коралл"
    elif pca_z < 0.03 and vector_rot_force > 5.0:
        verdict = "Плоский Аттрактор (Петля/Узел)"
    elif step_anomaly_ratio > 4.5 or abs(skewness) > 3.0:
        verdict = "Аномальный Сдвиг / Выброс"
    elif shannon_ent > 3.5 and hurst < 0.35:
        verdict = "Хаотичное Облако (Шум)"
    else:
        verdict = "Сложная динамическая структура"

    return {
        "ID": seq_id,
        "Название": seq_name,
        "Status": "Успешно",
        "Вердикт": verdict,
        "Энтропия_Шеннона": round(shannon_ent, 4),
        "Энтропия_Перестановок": round(perm_ent, 4),
        "Фрактал_Размерность_GP": round(corr_dim, 4),
        "Асимметрия_Сдвига": round(skewness, 4),
        "Эксцесс_Хвостов": round(kurtosis, 4),
        "Автокорреляция_Лаг1": round(ac_lag1, 4),
        "Херст_Хаотичность": round(hurst, 4),
        "Радиус_Облака": round(cloud_radius, 2),
        "Коэф_Сдвига_Аномалий": round(step_anomaly_ratio, 2),
        "Доля_Оси_X": round(pca_x, 4),
        "Доля_Оси_Y": round(pca_y, 4),
        "Доля_Оси_Z": round(pca_z, 4),
        "Сила_Закрутки_Ротора": round(vector_rot_force, 2),
        "Индекс_Сквозных_Дыр": round(has_hollow_holes, 4),
        "Коэф_Ветвления": round(branch_ratio, 4),
        "Частота_Фурье": main_freq
    }

# =====================================================================
# ГЛАВНЫЙ ПОТОКОВЫЙ КОНВЕЙЕР
# =====================================================================
if __name__ == "__main__":
    print("🚀 Запуск Великого Атласа OEIS (Числа + Названия)...")
    
    if not os.path.exists(INPUT_STRIPPED) or not os.path.exists(INPUT_NAMES):
        print("❌ ОШИБКА: Проверьте файлы в папке! Должны лежать stripped.gz и names.gz.")
        exit()

    print("📖 Загрузка словаря названий...")
    name_dict = {}
    with gzip.open(INPUT_NAMES, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split(' ', 1)
            if len(parts) == 2:
                name_dict[parts[0].strip()] = parts[1].strip()

    file_exists = os.path.isfile(OUTPUT_FILE)
    batch_data = []
    processed_count = 0
    start_time = time.time()
    
    print(f"📦 Потоковое потрошение базы цифр. Лимит: {LIMIT_SEQUENCES} рядов.")

    with gzip.open(INPUT_STRIPPED, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
                
            parts = line.split(',')
            seq_id = parts[0].strip()
            seq_name = name_dict.get(seq_id, "Без названия")
            
            raw_seq = []
            for item in parts[1:]:
                item_clean = item.strip()
                if item_clean and item_clean != '\n':
                    try:
                        raw_seq.append(int(item_clean))
                    except ValueError:
                        continue
            
            analysis = analyze_sequence(seq_id, seq_name, raw_seq)
            batch_data.append(analysis)
            processed_count += 1
            
            if len(batch_data) == BATCH_SIZE or processed_count >= LIMIT_SEQUENCES:
                df_batch = pd.DataFrame(batch_data)
                
                if not file_exists:
                    df_batch.to_csv(OUTPUT_FILE, index=False, mode='w', encoding="utf-8-sig")
                    file_exists = True
                else:
                    df_batch.to_csv(OUTPUT_FILE, index=False, mode='a', header=False, encoding="utf-8-sig")
                
                print(f"💾 [Батч сохранен!] Итого обработано реальных рядов: {processed_count}/{LIMIT_SEQUENCES}")
                batch_data = []
                time.sleep(0.3)
                
            if processed_count >= LIMIT_SEQUENCES:
                break

    end_time = time.time()
    print("\n" + "="*50)
    print("🎉 СУПЕР-АНАЛИЗ РЕАЛЬНОЙ ВСЕЛЕННОЙ ЧИСЕЛ ЗАВЕРШЕН!")
    print(f"⏱️ Время работы: {round(end_time - start_time, 2)} сек.")
    print(f"📊 Результаты сохранены в: {OUTPUT_FILE}")
    print("="*50)
