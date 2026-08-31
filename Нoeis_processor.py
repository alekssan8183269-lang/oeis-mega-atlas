import os
import time
import math
import gzip
import numpy as np
import pandas as pd

# =====================================================================
# НАСТРОЙКИ СВЕРХМОЩНОГО КОНВЕЙЕРА (Безопасно для i5 и 8GB ОЗУ)
# =====================================================================
BATCH_SIZE = 20           # Обрабатываем строго по 20 последовательностей за раз
EMBEDDING_DIM = 3         # Размерность пространства (3D-векторы: X, Y, Z)
INPUT_STRIPPED = "stripped.gz" 
INPUT_NAMES = "names.gz"       
OUTPUT_FILE = "oeis_mega_atlas_40fields.csv"

# Лимит на этот запуск (1000 для теста, или измените на 360000 для ВСЕЙ базы!)
LIMIT_SEQUENCES = 1000  

# Вспомогательная быстрая и безопасная функция корреляции Пирсона для лагов
def safe_correlation(x, y):
    if len(x) < 2 or len(y) < 2: return 0.0
    std_x, std_y = np.std(x), np.std(y)
    if std_x < 1e-8 or std_y < 1e-8: return 0.0
    cov = np.mean((x - np.mean(x)) * (y - np.mean(y)))
    corr = float(cov / (std_x * std_y))
    return 0.0 if np.isnan(corr) else corr

# =====================================================================
# ФУНКЦИЯ ПОЛНОГО МАТЕМАТИЧЕСКОГО ВСКРЫТИЯ (37 МЕТРИК / 40 КОЛОНОК)
# =====================================================================
def analyze_sequence(seq_id, seq_name, raw_sequence):
    seq = np.array(raw_sequence, dtype=float)
    seq = seq[np.isfinite(seq)]
    
    # Сложным фичам (особенно лагам до 5) нужно достаточное количество чисел
    if len(seq) < EMBEDDING_DIM + 15: 
        return {"ID": seq_id, "Название": seq_name, "Вердикт": "Пропущен (Слишком короткий ряд)", "Status": "Skip"}

    # Лог в консоль для отслеживания полета
    print(f"🚀 Потрошим: {seq_id} | Длина: {len(seq)} | {seq_name[:40]}...")

    # Построение 3D-траектории (Теорема Такенса)
    num_vectors = len(seq) - EMBEDDING_DIM + 1
    vectors = np.zeros((num_vectors, EMBEDDING_DIM))
    for i in range(EMBEDDING_DIM):
        vectors[:, i] = seq[i : i + num_vectors]

    diffs = np.diff(seq)
    n_len = len(seq)
    mean_val = np.mean(seq)
    std_val = np.std(seq) + 1e-8

    # -----------------------------------------------------------------
    # РАЗДЕЛ 1: СТАТИСТИКА ВЫСШИХ ПОРЯДКОВ И ПРОЦЕНТИЛИ (6 фич)
    # -----------------------------------------------------------------
    skewness = float(np.mean((seq - mean_val) ** 3) / (std_val ** 3))
    kurtosis = float(np.mean((seq - mean_val) ** 4) / (std_val ** 4)) - 3.0
    coef_variation = float(std_val / (abs(mean_val) + 1e-8))
    pct_75 = float(np.percentile(seq, 75))
    pct_95 = float(np.percentile(seq, 95))
    mean_step = np.mean(np.abs(diffs))
    step_anomaly_ratio = float(np.max(np.abs(diffs)) / (mean_step + 1e-8))

    # -----------------------------------------------------------------
    # РАЗДЕЛ 2: КВАНТОВАЯ И ДИНАМИЧЕСКАЯ ЭНТРОПИЯ (3 фичи)
    # -----------------------------------------------------------------
    _, counts = np.unique(seq, return_counts=True)
    probs = counts / n_len
    shannon_ent = float(-np.sum(probs * np.log2(probs + 1e-12)))

    patterns = []
    for i in range(n_len - 2):
        patterns.append(tuple(np.argsort(seq[i:i+3])))
    unique_pats, pat_counts = np.unique(patterns, axis=0, return_counts=True)
    perm_ent = float(-np.sum((pat_counts / len(patterns)) * np.log2((pat_counts / len(patterns)) + 1e-12)))

    # Приближенная энтропия микро-паттернов (Быстрый матричный аналог ApEn)
    try:
        sub_len = min(n_len, 40)
        m_diff = np.abs(seq[:sub_len, None] - seq[None, :sub_len])
        approx_ent = float(-np.mean(np.log(np.sum(m_diff < (0.2 * std_val), axis=1) / sub_len + 1e-12)))
    except:
        approx_ent = 0.0

    # -----------------------------------------------------------------
    # РАЗДЕЛ 3: ЭХО-ЛАГИ АВТОКОРРЕЛЯЦИИ (5 фич)
    # -----------------------------------------------------------------
    ac_lag1 = safe_correlation(seq[:-1], seq[1:])
    ac_lag2 = safe_correlation(seq[:-2], seq[2:])
    ac_lag3 = safe_correlation(seq[:-3], seq[3:])
    ac_lag4 = safe_correlation(seq[:-4], seq[4:])
    ac_lag5 = safe_correlation(seq[:-5], seq[5:])

    # -----------------------------------------------------------------
    # РАЗДЕЛ 4: СВЕРХГЛУБОКИЙ ФУРЬЕ-СПЕКТР (6 фич)
    # -----------------------------------------------------------------
    try:
        fft_vals = np.abs(np.fft.fft(seq))
        fft_half = fft_vals[1:n_len//2 + 1]
        fft_energy = float(np.sum(fft_half ** 2))
        main_freq = float(np.argmax(fft_half) + 1)
        max_amplitude = float(np.max(fft_half))
        median_freq = float(np.median(np.where(fft_half > (max_amplitude * 0.1))[0] + 1)) if len(fft_half) > 0 else 0.0
        fft_dispersion = float(np.std(fft_half))
        
        # Спектральная энтропия (чистота частот ряда)
        fft_probs = fft_half / (np.sum(fft_half) + 1e-12)
        spectral_ent = float(-np.sum(fft_probs * np.log2(fft_probs + 1e-12)))
    except:
        fft_energy, main_freq, max_amplitude, median_freq, fft_dispersion, spectral_ent = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    # -----------------------------------------------------------------
    # РАЗДЕЛ 5: ГЕОМЕТРИЯ ВЕКТОРНОЙ ЗМЕИ И ТЕНЗОРНЫЙ АНАЛИЗ (9 фич)
    # -----------------------------------------------------------------
    center = np.mean(vectors, axis=0)
    cloud_radius = float(np.mean(np.linalg.norm(vectors - center, axis=1)))
    
    # Полная физическая длина трехмерного следа змеи ряда
    snake_total_length = float(np.sum(np.linalg.norm(np.diff(vectors, axis=0), axis=1))) if len(vectors) > 1 else 0.0

    try:
        _, S, _ = np.linalg.svd(vectors - center, full_matrices=False)
        pca_x, pca_y, pca_z = float(S[0]/np.sum(S)), float(S[1]/np.sum(S)), float(S[2]/np.sum(S))
    except:
        pca_x, pca_y, pca_z = 0.33, 0.33, 0.33

    cross_products = np.cross(vectors[:-1], vectors[1:])
    vector_rot_force = float(np.mean(np.linalg.norm(cross_products, axis=1))) if len(cross_products) > 0 else 0.0

    start_end_dist = np.linalg.norm(vectors[0] - vectors[-1])
    has_hollow_holes = 1.0 / (start_end_dist + 1e-5)
    branch_ratio = safe_correlation(diffs[:-1], diffs[1:])

    try:
        sub_vecs = vectors[:40]
        dists = np.linalg.norm(sub_vecs[:, None, :] - sub_vecs[None, :, :], axis=-1)
        flat_dists = dists[np.triu_indices_from(dists, k=1)]
        r = np.median(flat_dists) * 0.5
        corr_sum = np.sum(flat_dists < r) / (len(flat_dists) + 1e-8)
        corr_dim = float(np.log(corr_sum + 1e-12) / np.log(r + 1e-12))
        corr_dim = min(max(corr_dim, 0.0), 3.0)
    except:
        corr_dim = 1.0

    # -----------------------------------------------------------------
    # РАЗДЕЛ 6: ФРАКТАЛЫ И ДЕВИАЦИЯ БЕНФОРДА (8 фич)
    # -----------------------------------------------------------------
    try:
        vals = seq - mean_val
        cum_vals = np.cumsum(vals)
        res_range = np.max(cum_vals) - np.min(cum_vals)
        hurst = math.log(res_range / (std_val)) / math.log(n_len)
        hurst = min(max(hurst, 0.0), 1.0)
    except:
        hurst = 0.5

    # Полный тест Бенфорда: отклонение первой цифры от логарифмического закона
    first_digits = [int(str(abs(int(x)))[0]) for x in raw_sequence if abs(int(x)) > 0 and str(abs(int(x)))[0].isdigit()]
    if len(first_digits) > 10:
        digit_counts = np.bincount(first_digits, minlength=10)[1:10]
        digit_probs = digit_counts / np.sum(digit_counts)
        benford_ideal = np.log10(1 + 1/np.arange(1, 10))
        benford_deviation = float(np.sum((digit_probs - benford_ideal) ** 2)) # Чем ближе к 0 - тем натуральнее ряд
        benford_pct_1 = float(digit_probs[0])
    else:
        benford_deviation = 1.0
        benford_pct_1 = 0.301

    # Ультимативный ИИ-вердикт на основе 37 фич
    if perm_ent < 1.0 and ac_lag1 > 0.85:
        verdict = "Абсолютный кристаллический тренд"
    elif shannon_ent > 4.2 and corr_dim > 2.4:
        verdict = "Гипер-коралл высшего порядка"
    elif pca_z < 0.02 and vector_rot_force > 15.0:
        verdict = "Космический закрученный Аттрактор"
    elif step_anomaly_ratio > 5.0 or abs(skewness) > 4.0:
        verdict = "Тектонический Сдвиг / Сбой Системы"
    elif spectral_ent > 4.0 and hurst < 0.25:
        verdict = "Высокоэнтропийный Белый Шум"
    elif benford_deviation < 0.02:
        verdict = "Натуральный закон Бенфорда"
    else:
        verdict = "Сверхсложная нелинейная форма"

    return {
        "ID": seq_id, "Название": seq_name, "Вердикт": verdict, "Status": "Успешно",
        "Длина_Ряда": n_len, "Среднее_Значение": round(mean_val, 2), "Станд_Отклонение": round(std_val, 2),
        "Коэф_Вариации": round(coef_variation, 4), "Асимметрия_Сдвига": round(skewness, 4), "Эксцесс_Хвостов": round(kurtosis, 4),
        "Процентиль_75": round(pct_75, 2), "Процентиль_95": round(pct_95, 2), "Коэф_Аномалий_Шага": round(step_anomaly_ratio, 2),
        "Энтропия_Шеннона": round(shannon_ent, 4), "Энтропия_Перестановок": round(perm_ent, 4), "Приближенная_Энтропия_ApEn": round(approx_ent, 4),
        "Автокорреляция_Лаг1": round(ac_lag1, 4), "Автокорреляция_Лаг2": round(ac_lag2, 4), "Автокорреляция_Лаг3": round(ac_lag3, 4),
        "Автокорреляция_Лаг4": round(ac_lag4, 4), "Автокорреляция_Лаг5": round(ac_lag5, 4), "Энергия_Спектра_Фурье": round(fft_energy, 2),
        "Главная_Частота_Фурье": main_freq, "Пик_Амплитуды_Фурье": round(max_amplitude, 2), "Медианная_Частота_Фурье": median_freq,
        "Дисперсия_Спектра_Фурье": round(fft_dispersion, 2), "Спектральная_Энтропия_Фурье": round(spectral_ent, 4), "Радиус_Векторного_Облака": round(cloud_radius, 2),
        "Физическая_Длина_Змеи": round(snake_total_length, 2), "Доля_Оси_PCA_X": round(pca_x, 4), "Доля_Оси_PCA_Y": round(pca_y, 4),
        "Доля_Оси_PCA_Z": round(pca_z, 4), "Сила_Ротора_Закрутки": round(vector_rot_force, 2), "Индекс_Сквозных_Дыр": round(has_hollow_holes, 4),

        "Коэф_Ветвления_Пирсона": round(branch_ratio, 4), "Фрактал_Размерность_GP": round(corr_dim, 4), "Показатель_Херста_Памяти": round(hurst, 4),
        "Девиация_Закона_Бенфорда": round(benford_deviation, 4), "Доля_Первых_Единиц_Бенфорда": round(benford_pct_1, 4)
    }
    
# =====================================================================
# ГЛАВНЫЙ АВТОНОМНЫЙ ДВИЖОК
# =====================================================================
if __name__ == "__main__":
    print("🛸 Инициализация Ультимативного 40-Поточного Мега-Атласа...")
    
    if not os.path.exists(INPUT_STRIPPED) or not os.path.exists(INPUT_NAMES):
        print("❌ ОШИБКА: Положите stripped.gz и names.gz (20-30 МБ) в папку с кодом!")
        exit()

    print("📖 Разворачиваем карту названий в памяти...")
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
    
    print(f"🎯 Поехали! Начинаем тотальную эксплуатацию базы. Цель: {LIMIT_SEQUENCES} рядов.")

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
            
            # Срабатывание батча строго по 20 штук - ОЗУ всегда чиста!
            if len(batch_data) == BATCH_SIZE or processed_count >= LIMIT_SEQUENCES:
                df_batch = pd.DataFrame(batch_data)
                
                if not file_exists:
                    df_batch.to_csv(OUTPUT_FILE, index=False, mode='w', encoding="utf-8-sig")
                    file_exists = True
                else:
                    df_batch.to_csv(OUTPUT_FILE, index=False, mode='a', header=False, encoding="utf-8-sig")
                
                print(f"💾 [БАТЧ ЗАПИСАН В CSV] Пройдено: {processed_count}/{LIMIT_SEQUENCES} рядов. ОЗУ полностью очищено.")
                batch_data = []
                time.sleep(0.3) # Остужаем i5
                
            if processed_count >= LIMIT_SEQUENCES:
                break

    end_time = time.time()
    print("\n" + "="*60)
    print("👑 ВЕЛИЧАЙШИЙ МАТЕМАТИЧЕСКИЙ АТЛАС УСПЕШНО СФОРМИРОВАН!")
    print(f"⏱️ Время тотального сканирования: {round(end_time - start_time, 2)} сек.")
    print(f"📊 40-колончатый шедевр сохранен в файл: {OUTPUT_FILE}")
    print("="*60)
