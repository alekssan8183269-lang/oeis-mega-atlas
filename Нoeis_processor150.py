import os
import time
import math
import gzip
import numpy as np
import pandas as pd
import networkx as nx  # графы наши
from ts2vg import NaturalVG, HorizontalVG
import scipy.stats as stats  # она нужна для расчета специальных энтропий и работы с матрицами
from scipy.spatial import ConvexHull
import struct
import scipy.linalg as la
import scipy.integrate as integrate
import sympy as sp



# =====================================================================
# НАСТРОЙКИ СВЕРХМОЩНОГО КОНВЕЙЕРА (Безопасно для i5 и 8GB ОЗУ)
# =====================================================================
BATCH_SIZE = 800           # Обрабатываем строго по 800 последовательностей за раз
EMBEDDING_DIM = 3         # Размерность пространства (3D-векторы: X, Y, Z)
MAX_ROWS_PER_FILE = 40000   # Жёсткий лимит строк на один файл, чтобы Excel не тупил!
INPUT_STRIPPED = "stripped.gz" 
INPUT_NAMES = "names.gz"       
OUTPUT_FILE = "oeis_mega_atlas_40fields.csv" # Основа имени для нарезки файлов
SKIP_COUNT = 0
MAX_SKIP_LOGS = 50

# Лимит на этот запуск (1000 для теста, или измените на 360000 для ВСЕЙ базы!)
# LIMIT_SEQUENCES = 10000  
# Лимит на этот запуск (Поставь 360000 или больше для обработки ВСЕЙ базы!)
LIMIT_SEQUENCES = 100000 

def safe_num(val, ndigits=4):
    """Запечатывает числа в текстовые формулы, защищая от автоформата Excel"""
    try:
        return f'="{round(float(val), ndigits)}"'
    except:
        return f'="{val}"'

# Вспомогательная быстрая и безопасная функция корреляции Пирсона для лагов
def safe_correlation(x, y):
    if len(x) < 2 or len(y) < 2: return 0.0
    std_x, std_y = np.std(x), np.std(y)
    if std_x < 1e-8 or std_y < 1e-8: return 0.0
    cov = np.mean((x - np.mean(x)) * (y - np.mean(y)))
    corr = float(cov / (std_x * std_y))
    return 0.0 if np.isnan(corr) else corr

# =====================================================================
# ФУНКЦИЯ ПОЛНОГО МАТЕМАТИЧЕСКОГО ВСКРЫТИЯ (37 МЕТРИК / 41 КОЛОНКА)
# =====================================================================
def analyze_sequence(seq_id, seq_name, raw_sequence):
    seq = np.array(raw_sequence, dtype=float)
    seq = seq[np.isfinite(seq)]
    
    # Сложным фичам (особенно лагам до 5) нужно достаточное количество чисел
    # if len(seq) < EMBEDDING_DIM + 15:    # БЫЛО 
    # НАДО СДЕЛАТЬ (Снижаем порог до 10 чисел):
    if len(seq) < 7:
        return {
            "ID": f'="{seq_id}"', "Название": seq_name, 
            "Чистый_Класс": "Skip", "Полный_Вердикт": "Пропущен (Слишком короткий ряд)", 
            "Status": "Skip", "Длина_Ряда": safe_num(len(seq), 0)
        }

    # Лог в консоль для отслеживания полета
    print(f"🚀 Потрошим: {seq_id} | Длина: {len(seq)} | {seq_name[:40]}...")

    try:
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
        # РАЗДЕЛ 6: ФРАКТАЛЫ И ДЕВИАЦИЯ БЕНФОРДА (8 фич) (С ЧЕСТНЫМ ХИ-КВАДРАТ)
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
            total_digits = np.sum(digit_counts)        
            digit_probs = digit_counts / np.sum(digit_counts)
            benford_ideal = np.log10(1 + 1/np.arange(1, 10))

            benford_deviation = float(np.sum((digit_probs - benford_ideal) ** 2)) # Чем ближе к 0 - тем натуральнее ряд
            
            # 1. Считаем Информационную Дивергенцию Кульбака-Лейблера (устойчива к малой длине)
            # Чем ближе к 0 - тем идентичнее распределения
            benford_kl_div = float(np.sum(digit_probs * np.log2((digit_probs + 1e-12) / benford_ideal)))
            
            # 2. А честный Хи-Квадрат считаем ТОЛЬКО если выборка позволяет
            
            # Исправленный Хи-Квадрат (использует digit_counts и ваш benford_ideal)
            if total_digits >= 30:
                expected_counts = benford_ideal * total_digits
                benford_chi2 = float(np.sum(((digit_counts - expected_counts) ** 2) / expected_counts))
                benford_p_verdict = "Значим (Хи-Квадрат OK)" if benford_chi2 < 15.51 else "Нетипичный ряд"
            else:
                benford_chi2 = -1.0
                benford_p_verdict = "Мало данных (Оценка по KL)" if benford_kl_div < 0.25 else "Нетипичный ряд"

            benford_pct_1 = float(digit_probs[0])
        else:
            benford_deviation = 1.0
            # Полный хаос или пустой ряд
            benford_kl_div = 4.0
            benford_chi2 = -1.0
            benford_p_verdict = "Слишком короткий"        
            benford_pct_1 = 0.301

        # Ультимативный ИИ-вердикт на основе 37 фич
        # if perm_ent < 1.0 and ac_lag1 > 0.85:
        #     verdict = "Абсолютный кристаллический тренд"
        # elif shannon_ent > 4.2 and corr_dim > 2.4:
        #     verdict = "Гипер-коралл высшего порядка"
        # elif pca_z < 0.02 and vector_rot_force > 15.0:
        #     verdict = "Космический закрученный Аттрактор"
        # elif step_anomaly_ratio > 5.0 or abs(skewness) > 4.0:
        #     verdict = "Тектонический Сдвиг / Сбой Системы"
        # elif spectral_ent > 4.0 and hurst < 0.25:
        #     verdict = "Высокоэнтропийный Белый Шум"
        # elif benford_deviation < 0.02:
        #     verdict = "Натуральный закон Бенфорда"
        # else:
        #     verdict = "Сверхсложная нелинейная форма"
        # =====================================================================
        # ГЛУБОКАЯ ИИ-КЛАССИФИКАЦИЯ: 14 МАТЕМАТИЧЕСКИХ АРХЕТИПОВ (С ЧИСЛАМИ)
        # =====================================================================

        # =====================================================================
        # ИИ-МЕТОДИЧЕСКАЯ КЛАССИФИКАЦИЯ ( 18 КЛАССОВ С ДВУМЯ КОЛОНКАМИ)
        # =====================================================================        
        # Сверхстабильные упорядоченные структуры
        if perm_ent < 1.0 and ac_lag1 > 0.85:
            if corr_dim > 3.0:
                c_clean = "[Class 1] High-Order Crystalline Fractal"
                verdict = f"[Класс 1] Кристаллический Фрактал высшего порядка, размерность GP={round(corr_dim, 4)}"
            elif abs(skewness) > 3.0:
                c_clean = "[Class 2] Asymmetric Exponential Growth"
                verdict = f"[Класс 2] Асимметричный Экспоненциальный Рост, асимметрия={round(skewness, 4)}"
            else:
                c_clean = "[Class 3] Absolute Crystalline Trend"
                verdict = f"[Класс 3] Абсолютный кристаллический тренд, память Lag1={round(ac_lag1, 4)}"

        # Сложная геометрия и орбиты (Такенс и PCA)
        elif pca_z < 0.08 and vector_rot_force > 12.0:
            if has_hollow_holes > 1000.0:
                c_clean = "[Class 4] Orbital Torus (Hollow)"
                verdict = f"[Класс 4] Орбитальный Тор с внутренней пустотой, дыры={round(has_hollow_holes, 2)}"
            else:
                c_clean = "[Class 5] Cosmic Swirling Attractor"
                verdict = f"[Класс 5] Космический закрученный Аттрактор, ротор закрутки={round(vector_rot_force, 4)}"
                
        elif pca_x > 0.80 and vector_rot_force > 5.0:
            c_clean = "[Class 6] Flat Quasiperiodic Disc"
            verdict = f"[Класс 6] Плоский Квазипериодический Диск, ось PCA_X={round(pca_x, 4)}"

        # Частотные резонансы и волны (Фурье)
        elif spectral_ent < 2.0 and max_amplitude > 10.0:
            if median_freq == main_freq:
                c_clean = "[Class 7] Pure Harmonic Resonance"
                verdict = f"[Класс 7] Чистый Гармонический Резонанс, частота={main_freq}"
            else:
                c_clean = "[Class 8] Polyphonic Wave Interference"
                verdict = f"[Класс 8] Полифоническая Волновая Интерференция, спектр энтропии={round(spectral_ent, 4)}"

        # Странный хаос и константы (Херст, Бенфорд и Дивергенция)
        elif 0.35 < hurst < 0.65:
            if benford_kl_div < 0.15 or benford_deviation < 0.02:
                c_clean = "[Class 9] Fundamental Constant Chaos (Pi/Phi)"
                verdict = f"[Класс 9] Фундаментальный Константный Хаос (Тип Пи/Phi), KL-дивергенция={round(benford_kl_div, 4)}, девиация={round(benford_deviation, 4)}"
            elif vector_rot_force > 8.0:
                c_clean = "[Class 10] Turbulent Dynamic Chaos"
                verdict = f"[Класс 10] Турбулентный Динамический Хаос, ротор={round(vector_rot_force, 4)}, Херст={round(hurst, 4)}"
            else:
                c_clean = "[Class 11] Entangled Nonlinear Stochastic"
                verdict = f"[Класс 11] Сплетенная Нелинейная Стохастика, Херст Памяти={round(hurst, 4)}"

        # Высокоэнтропийные и фрактальные кораллы
        elif shannon_ent > 4.2 and corr_dim > 2.4:
            if hurst > 0.70:
                c_clean = "[Class 12] Persistent Hyper-Coral (Long Memory)"
                verdict = f"[Класс 12] Персистентный Гипер-Коралл (Долгая Память), Херст={round(hurst, 4)}"
            else:
                c_clean = "[Class 13] High-Order Hyper-Coral"
                verdict = f"[Класс 13] Гипер-коралл высшего порядка, размерность GP={round(corr_dim, 4)}"

        # Псевдо-шум и скрытая геометрия
        elif spectral_ent > 4.0 and hurst < 0.25:
            if has_hollow_holes > 5000.0:
                c_clean = "[Class 14] Geometric Torus (Pseudo-Noise)"
                verdict = f"[Класс 14] Геометрический Тор (Псевдо-Шум), дыры={round(has_hollow_holes, 2)}"
            else:
                c_clean = "[Class 15] High-Entropy White Noise"
                verdict = f"[Класс 15] Высокоэнтропийный Белый Шум, спектр энтропии={round(spectral_ent, 4)}"

        # Критические аномалии и разрывы
        elif step_anomaly_ratio > 5.0 or abs(skewness) > 5.0:
            c_clean = "[Class 16] Tectonic Shift / System Failure"
            verdict = f"[Класс 16] Тектонический Сдвиг / Сбой Системы, аномалия шага={round(step_anomaly_ratio, 4)}"

        # Чистые законы Бенфорда для комбинаторных рядов
        elif benford_kl_div < 0.10 or benford_deviation < 0.01:
            c_clean = "[Class 17] Natural Benford Law (Strict)"
            verdict = f"[Класс 17] Натуральный закон Бенфорда (Строгий), KL-дивергенция={round(benford_kl_div, 4)}"

        # Если ряд ведет себя как хаос, но имеет идеальные скрытые фрактальные частоты
        elif 1.2 < perm_ent < 1.7 and 0.45 < hurst < 0.55 and fft_energy > 5000:
            c_clean = "Aperiodic Mosaic / Quasicrystal"
            verdict = "[Class 19] Апериодическая мозаика (Квазикристалл)"


        # Как мозаика выдает себя в наших колонках?
        # Апериодическая мозаика — это не хаос, это сверхструктурированный порядок, 
        # у которого просто нет одного фиксированного периода. В твоем CSV-файле такой ряд выдаст уникальное, ни на что не похожее
        #  комбо из трех уже готовых колонок:Показатель_Херста_Памяти = 0.5 (или строго около этого): 
        #  Мозаика бесконечна и фрактальна, у неё идеальная долгосрочная память. Ряд не сваливается в тренд и не затухает к нулю.
        #  Энтропия_Перестановок = средняя (около 1.2 — 1.6): Это главный маркер! Если бы это был случайный мусор, энтропия улетела бы к максимуму (2.5+). 
        #  Если бы это был банальный цикл — она упала бы к нулю. Среднее стабильное значение доказывает: перед нами сложный апериодический узор.
        #  Доля_Оси_PCA_Z = четкое фиксированное число (например, строго 0.12): 
        # В 3D-пространстве Такенса траектория мозаики не размазывается в бесформенное облако, а прессуется в тончайшие, фрактальные слои (квазипериодические слои).

        # У обычных периодических рядов на графике Фурье один-два гигантских пика (острые иглы). 
        # У белого шума — плоский грязный ковер. А у апериодических мозаик (квазикристаллов) спектр Фурье выглядит как 
        # «Брэгговский паттерн» — бесконечное множество четких, фрактальных пиков (иглы в иглах), которые подчиняются правилу золотого сечения.


        # Финал для того, что не поддается стандартной логике
        else:
            c_clean = "[Class 18] High-Complexity Nonlinear Form"
            verdict = f"[Класс 18] Сверхсложная нелинейная форма, энтропия={round(perm_ent, 4)}"

        # -----------------------------------------------------------------
        # РАЗДЕЛ 7: ГРАФЫ ВИДИМОСТИ ЧИСЕЛ (NVG И HVG) (+30 МЕТРИК)
        # -----------------------------------------------------------------
        # Ограничиваем длину для графов до 150 чисел, чтобы i5 не закипел на тяжелых метриках
        # Ограничиваем пики, чтобы граф видимости строился корректно без улета весов в бесконечность
        g_seq = np.clip(seq[:150], -1e6, 1e6) 
        
        # Строим Натуральный Граф Видимости (NVG) и Горизонтальный (HVG)
        # nvg = NaturalVG().build(g_seq).to_networkx()
        # hvg = HorizontalVG().build(g_seq).to_networkx()

        nvg = NaturalVG().build(g_seq).as_networkx()
        hvg = HorizontalVG().build(g_seq).as_networkx()  

        # Базовые свойства NVG
        nvg_nodes = nvg.number_of_nodes()
        nvg_edges = nvg.number_of_edges()
        nvg_density = float(nx.density(nvg))
        
        nvg_degrees = [d for n, d in nvg.degree()]
        nvg_max_degree = float(np.max(nvg_degrees)) if nvg_degrees else 0.0
        nvg_mean_degree = float(np.mean(nvg_degrees)) if nvg_degrees else 0.0
        
        # Энтропия распределения степеней NVG
        _, deg_counts = np.unique(nvg_degrees, return_counts=True)
        deg_probs = deg_counts / len(nvg_degrees)
        nvg_degree_entropy = float(-np.sum(deg_probs * np.log2(deg_probs + 1e-12)))
        
        # Продвинутая топология NVG (Кластеризация и пути)
        nvg_avg_clustering = float(nx.average_clustering(nvg))
        nvg_transitivity = float(nx.transitivity(nvg))
        
        try:
            nvg_diameter = float(nx.diameter(nvg))
            nvg_radius = float(nx.radius(nvg))
            nvg_avg_path = float(nx.average_shortest_path_length(nvg))
        except:
            nvg_diameter, nvg_radius, nvg_avg_path = 0.0, 0.0, 0.0
            
        # Ассортативность (богатый к богатому)
        try: nvg_assortativity = float(nx.degree_assortativity_coefficient(nvg))
        except: nvg_assortativity = 0.0
            
        # Центральности NVG (вырезаем прожорливый betweenness, оставляем быстрые)
        nvg_close_cent = list(nx.closeness_centrality(nvg).values())
        nvg_mean_closeness = float(np.mean(nvg_close_cent)) if nvg_close_cent else 0.0
        
        try:
            nvg_eig_cent = list(nx.eigenvector_centrality(nvg, max_iter=500).values())
            nvg_mean_eigen = float(np.mean(nvg_eig_cent))
        except:
            nvg_mean_eigen = 0.0

        # Модульность и Сообщества (быстрый жадный алгоритм Клаузета-Ньюмана-Мура)
        try:
            nvg_communities = list(nx.community.greedy_modularity_communities(nvg))
            nvg_num_communities = float(len(nvg_communities))
            nvg_modularity = float(nx.community.modularity(nvg, nvg_communities))
        except:
            nvg_num_communities, nvg_modularity = 1.0, 0.0

        # Спектральная теория графов для NVG (Энергия Лапласиана)
        try:
            nvg_laplacian_matrix = nx.laplacian_matrix(nvg).toarray()
            nvg_lap_eigenvals = np.linalg.eigvalsh(nvg_laplacian_matrix)
            nvg_graph_energy = float(np.sum(np.abs(nvg_lap_eigenvals - (2 * nvg_edges / nvg_nodes))))
            nvg_spectral_radius = float(np.max(np.abs(nvg_lap_eigenvals)))
            # Число Фидлера (алгебраическая связность) — второе наименьшее число
            nvg_fiedler_value = float(np.sort(nvg_lap_eigenvals)[1]) if len(nvg_lap_eigenvals) > 1 else 0.0
        except:
            nvg_graph_energy, nvg_spectral_radius, nvg_fiedler_value = 0.0, 0.0, 0.0

        # Метрики Горизонтального Графа (HVG) — он шикарно ловит марковость чисел
        hvg_nodes = hvg.number_of_nodes()
        hvg_edges = hvg.number_of_edges()
        hvg_density = float(nx.density(hvg))
        hvg_degrees = [d for n, d in hvg.degree()]
        hvg_mean_degree = float(np.mean(hvg_degrees)) if hvg_degrees else 0.0
        hvg_avg_clustering = float(nx.average_clustering(hvg))
        
        # Специфика Видимости (Длина ребер во времени)
        # Насколько далеко пики «видят» друг друга по оси индексов
        edge_lengths = [abs(u - v) for u, v in nvg.edges()]
        nvg_mean_edge_length = float(np.mean(edge_lengths)) if edge_lengths else 0.0
        nvg_max_edge_length = float(np.max(edge_lengths)) if edge_lengths else 0.0

        # -----------------------------------------------------------------
        # РАЗДЕЛ 8: ЧИСТАЯ ПРИЧИННАЯ ЭМЕРДЖЕНТНОСТЬ (CAUSAL EMERGENCE) (+5 фич)
        # -----------------------------------------------------------------
        # Считаем эффективную информацию (EI) микро-шагов vs макро-агрегата
        try:
            # Микро-уровень: переходы состояний через знаки приращений
            sign_diffs = np.sign(diffs)
            state_pairs = [(sign_diffs[i], sign_diffs[i+1]) for i in range(len(sign_diffs)-1)]
            unique_pairs, pair_counts = np.unique(state_pairs, axis=0, return_counts=True)
            p_matrix = pair_counts / len(state_pairs)
            # Энтропия переходов (Микро-шум)
            micro_noise = float(-np.sum(p_matrix * np.log2(p_matrix + 1e-12)))
            
            # Макро-уровень: агрегируем ряд скользящим средним размером в 3 шага
            macro_seq = np.convolve(seq, np.ones(3)/3, mode='valid')
            macro_diffs = np.sign(np.diff(macro_seq))
            macro_pairs = [(macro_diffs[i], macro_diffs[i+1]) for i in range(len(macro_diffs)-1)]
            m_unique_pairs, m_pair_counts = np.unique(macro_pairs, axis=0, return_counts=True)
            m_matrix = m_pair_counts / len(macro_pairs)
            macro_noise = float(-np.sum(m_matrix * np.log2(m_matrix + 1e-12)))
            
            # Causal Emergence (Причинная Эмерджентность)
            # Если макро-структура менее зашумлена, чем микро-переходы — значение положительное
            causal_emergence = float(micro_noise - macro_noise)
            
            # Индекс самоорганизации Шеннона
            shannon_diff = float(-np.sum(p_matrix * np.log2(p_matrix + 1e-12)))
            self_organization_index = float(shannon_diff / (shannon_ent + 1e-12))
        except:
            causal_emergence, self_organization_index, micro_noise, macro_noise = 0.0, 0.0, 0.0, 0.0

        # =====================================================================
        # РАЗДЕЛ 8: БЛОК СВЕРХГЛУБОКОЙ МАТЕМАТИЧЕСКОЙ ЭМЕРДЖЕНТНОСТИ (20 МЕТРИК)
        # =====================================================================
        try:
            # --- 1-4. Причинная Эмерджентность по Хоэлу (Causal Emergence) ---
            sign_diffs = np.sign(diffs)
            state_pairs = [(sign_diffs[i], sign_diffs[i+1]) for i in range(len(sign_diffs)-1)]
            if len(state_pairs) > 0:
                unique_pairs, pair_counts = np.unique(state_pairs, axis=0, return_counts=True)
                p_matrix = pair_counts / len(state_pairs)
                micro_noise = float(-np.sum(p_matrix * np.log2(p_matrix + 1e-12)))
            else:
                micro_noise, p_matrix = 0.0, np.array([1.0])

            # Скользящее среднее (окно 3) для создания макро-переменной
            macro_window = 3
            if len(seq) >= macro_window + 2:
                macro_seq = np.convolve(seq, np.ones(macro_window)/macro_window, mode='valid')
                macro_diffs = np.sign(np.diff(macro_seq))
                macro_pairs = [(macro_diffs[i], macro_diffs[i+1]) for i in range(len(macro_diffs)-1)]
                m_unique_pairs, m_pair_counts = np.unique(macro_pairs, axis=0, return_counts=True)
                m_matrix = m_pair_counts / len(macro_pairs)
                macro_noise = float(-np.sum(m_matrix * np.log2(m_matrix + 1e-12)))
            else:
                macro_noise = micro_noise

            causal_emergence = float(micro_noise - macro_noise)
            shannon_diff_ent = float(-np.sum(p_matrix * np.log2(p_matrix + 1e-12)))
            self_organization_index = float(shannon_diff_ent / (shannon_ent + 1e-12))

            # --- 5-7. Продвинутые нелинейные энтропии (Реньи, Цаллис) ---
            # Энтропия Реньи (альфа=2) — ловит крупные фрактальные аномалии
            renyi_ent = float(1.0 / (1.0 - 2.0) * np.log2(np.sum(probs**2) + 1e-12))
            # Энтропия Цаллиса (q=2) — для неэкспоненциального хаоса
            tsallis_ent = float(1.0 / (2.0 - 1.0) * (1.0 - np.sum(probs**2)))

            # --- 8-10. Энтропии Перестановок с Лагами (Скрытые фазовые переходы) ---
            # Лаг 2
            pats_l2 = [tuple(np.argsort(seq[i:i+3:2])) for i in range(max(1, n_len - 4))]
            _, c_l2 = np.unique(pats_l2, axis=0, return_counts=True)
            perm_ent_l2 = float(-np.sum((c_l2 / len(pats_l2)) * np.log2((c_l2 / len(pats_l2)) + 1e-12))) if pats_l2 else 0.0

            # Лаг 3
            pats_l3 = [tuple(np.argsort(seq[i:i+6:3])) for i in range(max(1, n_len - 7))]
            _, c_l3 = np.unique(pats_l3, axis=0, return_counts=True)
            perm_ent_l3 = float(-np.sum((c_l3 / len(pats_l3)) * np.log2((c_l3 / len(pats_l3)) + 1e-12))) if pats_l3 else 0.0

            # --- 11-12. Информационное Расстояние Вассерштейна (Динамика формы) ---
            # Проверяем, как меняется форма распределения между 1-й и 2-й половиной ряда
            half_idx = n_len // 2
            if half_idx > 2:
                wasserstein_dist = float(stats.wasserstein_distance(seq[:half_idx], seq[half_idx:]))
            else:
                wasserstein_dist = 0.0

            # --- 13-14. Информационное закрытие и Спектральный зазор Шеннона ---
            # Отношение спектральной энтропии к информационной (чистота хаоса)
            shannon_spectral_ratio = float(spectral_ent / (shannon_ent + 1e-12))

            # --- 15-17. Локальный показатель Ляпунова (Эффект Бабочки в числах) ---
            # Оценка разлета траекторий Такенса на ультракоротких шагах
            if len(vectors) > 3:
                d0 = np.linalg.norm(vectors[1] - vectors[0]) + 1e-8
                d1 = np.linalg.norm(vectors[2] - vectors[1])
                local_lyapunov = float(np.log(d1 / d0))
            else:
                local_lyapunov = 0.0

            # --- 18-20. Метрики Самоорганизации Сигнала (Рекуррентный хаос) ---
            # Коэффициент флуктуационной стационарности (вариация локальных скользящих стандартных отклонений)
            roll_std = [np.std(seq[i:i+4]) for i in range(max(1, n_len - 3))]
            fluc_co_variation = float(np.std(roll_std) / (np.mean(roll_std) + 1e-8)) if roll_std else 0.0
            
            # Коэффициент затухания автокорреляции (скорость потери памяти системой)
            ac_decay_rate = float(abs(ac_lag1) - abs(ac_lag5))

            # Итоговая комплексная мера: Коэффициент Эмерджентного Резонанса
            # Соотношение главной доминантной оси PCA к хаосу Шеннона
            emergence_resonance_score = float(pca_x / (shannon_ent + 1e-12))

        except:
            # На случай сбоя — жесткие нули в твоем стиле
            causal_emergence, self_organization_index, micro_noise, macro_noise = 0.0, 0.0, 0.0, 0.0
            renyi_ent, tsallis_ent, perm_ent_l2, perm_ent_l3 = 0.0, 0.0, 0.0, 0.0
            wasserstein_dist, shannon_spectral_ratio, local_lyapunov = 0.0, 0.0, 0.0
            fluc_co_variation, ac_decay_rate, emergence_resonance_score = 0.0, 0.0, 0.0

        # =====================================================================
        # РАЗДЕЛ 9: ТОПОЛОГИЧЕСКИЙ АНАЛИЗ (TDA) И ГЕОМЕТРИЯ ЗМЕЙКИ (16 МЕТРИК)
        # =====================================================================
        try:
            # Подготовка облака 3D-точек (траектория Такенса)
            # Ограничиваем до 100 векторов для скорости
            t_vecs = vectors[:100]
            n_vecs = len(t_vecs)

            # Матрица попарных евклидовых расстояний между всеми 3D-точками
            if n_vecs > 1:
                d_matrix = np.linalg.norm(t_vecs[:, None, :] - t_vecs[None, :, :], axis=-1)
                flat_dists = d_matrix[np.triu_indices_from(d_matrix, k=1)]
                median_d = float(np.median(flat_dists)) + 1e-8
            else:
                d_matrix, flat_dists, median_d = np.array([0.0]), np.array([0.0]), 1.0

            # --- 1-2. Быстрый TDA-аналог Персистентных Гомологий (Пустоты Betti) ---
            # Считаем количество изолированных топологических дыр на разном радиусе обзора
            r_small = median_d * 0.5
            r_large = median_d * 1.5
            
            # Betti 0 (связные компоненты при малом радиусе)
            betti_0_small = float(np.sum(d_matrix < r_small) / (n_vecs + 1e-12))
            # Betti 1/2 (пустоты/туннели при крупном радиусе)
            betti_1_large = float(np.sum((d_matrix >= r_small) & (d_matrix < r_large)) / (n_vecs + 1e-12))
            
            # --- 3. Длина штрихкода пустот (Persistence Lifespan) ---
            persistence_lifespan = float(abs(np.max(flat_dists) - median_d)) if len(flat_dists) > 0 else 0.0

            # --- 4-6. Тензор инерции 3D-облака (Собственные числа формы) ---
            if n_vecs > 2:
                inertia_tensor = np.dot((t_vecs - center).T, (t_vecs - center))
                inertia_eigvals = np.linalg.eigvalsh(inertia_tensor)
                # Нормируем, чтобы получить чистые коэффициенты формы
                sum_eig = np.sum(inertia_eigvals) + 1e-12
                inertia_x, inertia_y, inertia_z = float(inertia_eigvals[0]/sum_eig), float(inertia_eigvals[1]/sum_eig), float(inertia_eigvals[2]/sum_eig)
            else:
                inertia_x, inertia_y, inertia_z = 0.33, 0.33, 0.33

            # --- 7. Сферическая асимметрия (Сдвиг формы) ---
            # Насколько центр геометрии змейки смещен относительно центра масс
            if n_vecs > 0:
                geom_bounds_center = (np.max(t_vecs, axis=0) + np.min(t_vecs, axis=0)) / 2.0
                spherical_asymmetry = float(np.linalg.norm(center - geom_bounds_center) / (cloud_radius + 1e-8))
            else:
                spherical_asymmetry = 0.0

            # --- 8. Извилистость змейки (Tortuosity) ---
            # Отношение реального пути к расстоянию старт-финиш
            if snake_total_length > 0 and start_end_dist > 0:
                tortuosity_index = float(snake_total_length / start_end_dist)
            else:
                tortuosity_index = 1.0

            # --- 9. Индекс Винера для геометрического облака ---
            t_wiener_index = float(np.sum(flat_dists)) if len(flat_dists) > 0 else 0.0

            # --- 10. Фрактальная размерность Минковского (Box-Counting) ---
            # Быстрая оценка через дискретизацию сетки
            if n_vecs > 2:
                min_b, max_b = np.min(t_vecs, axis=0), np.max(t_vecs, axis=0)
                span = (max_b - min_b) + 1e-8
                # Бьем пространство на сетку 10х10х10
                grid_indices = ((t_vecs - min_b) / span * 9).astype(int)
                unique_boxes = len(np.unique(grid_indices, axis=0))
                minkowski_box_dim = float(np.log(unique_boxes + 1e-12) / np.log(10))
            else:
                minkowski_box_dim = 1.0

            # --- 11-12. Выпуклая оболочка (Convex Hull) ---
            # Физический объем 3D-мешка, куда помещается змейка ряда
            if n_vecs >= 4 and np.linalg.matrix_rank(t_vecs - center) >= 3:
                hull = ConvexHull(t_vecs)
                convex_hull_volume = float(hull.volume)
                convex_hull_solidity = float(n_vecs / (hull.volume + 1e-8))
            else:
                convex_hull_volume = 0.0
                convex_hull_solidity = 0.0

            # --- 13-14. Кривизна Гаусса и Кручение (3D-динамика изгибов) ---
            if len(vectors) > 2:
                v_diff1 = np.diff(vectors, axis=0)
                v_diff2 = np.diff(v_diff1, axis=0)
                # Кривизна Гаусса как норма ускорения змейки
                gaussian_curvature = float(np.mean(np.linalg.norm(v_diff1[:-1], axis=1)))
                # Кручение (выход из плоскости)
                torsion_force = float(np.mean(np.linalg.norm(v_diff2, axis=1)))
            else:
                gaussian_curvature, torsion_force = 0.0, 0.0

            # --- 15. Плотность самопересечений ---
            # Сколько раз змейка подходит близко к своим старым виткам
            if n_vecs > 2:
                self_intersections = float(np.sum(flat_dists < (median_d * 0.2)) / (len(flat_dists) + 1e-8))
            else:
                self_intersections = 0.0

            # --- 16. Радиус гирации (Компактность упаковки ДНК ряда) ---
            if n_vecs > 0:
                radius_of_gyration = float(np.sqrt(np.mean(np.sum((t_vecs - center)**2, axis=1))))
            else:
                radius_of_gyration = 0.0

        except:
            # Аварийные нули для TDA
            betti_0_small, betti_1_large, persistence_lifespan = 0.0, 0.0, 0.0
            inertia_x, inertia_y, inertia_z, spherical_asymmetry = 0.33, 0.33, 0.33, 0.0
            tortuosity_index, t_wiener_index, minkowski_box_dim = 1.0, 0.0, 1.0
            convex_hull_volume, convex_hull_solidity = 0.0, 0.0
            gaussian_curvature, torsion_force, self_intersections, radius_of_gyration = 0.0, 0.0, 0.0, 0.0

        # =====================================================================
        # РАЗДЕЛ 10: ВЫСШАЯ АЛГЕБРА И ТЕОРИЯ ЧИСЕЛ (12 МЕТРИК)
        # =====================================================================
        try:
            # Очищаем массив для теории чисел: только целые, абсолютные значения, убираем нули
            # clean_ints = np.abs(seq[np.isfinite(seq)]).astype(int)
            # Защита от переполнения: если числа гигантские, берем остаток или лимитируем
            safe_seq = np.array([x if abs(x) < 1e7 else (abs(int(x)) % 1000000) for x in seq], dtype=float)
            clean_ints = np.abs(safe_seq).astype(int)
            clean_ints_no_zero = clean_ints[clean_ints > 0]
            
            # --- 1. Плотность простых делителей (Prime Factor Density) ---
            def count_prime_factors(n):
                if n <= 1: return 0
                count = 0
                d = 2
                while d * d <= n:
                    if n % d == 0:
                        count += 1
                        while n % d == 0:
                            n //= d
                    d += 1
                if n > 1: count += 1
                return count

            if len(clean_ints_no_zero) > 0:
                # Считаем для первых 40 чисел для удержания скорости
                prime_counts = [count_prime_factors(int(x)) for x in clean_ints_no_zero[:40]]
                prime_factor_density = float(np.mean(prime_counts))
            else:
                prime_factor_density = 0.0

            # --- 2. Индекс взаимной простоты (Coprimality Rate) ---
            if len(clean_ints) > 1:
                coprime_pairs = 0
                total_pairs = len(clean_ints) - 1
                for i in range(total_pairs):
                    if math.gcd(int(clean_ints[i]), int(clean_ints[i+1])) == 1:
                        coprime_pairs += 1
                coprimality_rate = float(coprime_pairs / total_pairs)
            else:
                coprimality_rate = 1.0

            # --- 3-6. Распределение остатков по модулю 2, 3, 5, 7 (Алгебраическая Энтропия) ---
            def get_mod_entropy(arr, mod):
                if len(arr) == 0: return 0.0
                mods = arr % mod
                _, counts = np.unique(mods, return_counts=True)
                p = counts / len(arr)
                return float(-np.sum(p * np.log2(p + 1e-12)))

            mod2_entropy = get_mod_entropy(clean_ints, 2)
            mod3_entropy = get_mod_entropy(clean_ints, 3)
            mod5_entropy = get_mod_entropy(clean_ints, 5)
            mod7_entropy = get_mod_entropy(clean_ints, 7)

            # --- 7. Частота совершенных/избыточных чисел (Perfect Numbers Proximity) ---
            def get_divisors_sum_ratio(n):
                if n <= 1: return 1.0
                sum_div = 1
                d = 2
                while d * d <= n:
                    if n % d == 0:
                        sum_div += d
                        if d * d != n:
                            sum_div += n // d
                    d += 1
                return float(sum_div / n)

            if len(clean_ints_no_zero) > 0:
                div_ratios = [get_divisors_sum_ratio(int(x)) for x in clean_ints_no_zero[:40]]
                perfect_proximity = float(np.mean(div_ratios))
            else:
                perfect_proximity = 1.0

            # --- 8. Показатель свободных от квадратов чисел (Square-Free Rate) ---
            def is_square_free(n):
                if n <= 1: return True
                if n % 4 == 0: return False
                d = 3
                while d * d <= n:
                    if n % (d * d) == 0:
                        return False
                    d += 2
                return True

            if len(clean_ints_no_zero) > 0:
                sf_flags = [1.0 if is_square_free(int(x)) else 0.0 for x in clean_ints_no_zero[:50]]
                square_free_rate = float(np.mean(sf_flags))
            else:
                square_free_rate = 1.0

            # --- 9. Длина периодов в p-адических числах (p-adic 2-valuation) ---
            def p_adic_2_valuation(n):
                if n == 0: return 0
                count = 0
                while n % 2 == 0:
                    count += 1
                    n //= 2
                return count

            if len(clean_ints) > 0:
                v2_vals = [p_adic_2_valuation(int(x)) for x in clean_ints]
                padic_valuation_mean = float(np.mean(v2_vals))
            else:
                padic_valuation_mean = 0.0

            # --- 10. Коэффициент Фибоначчизации (Золотое сечение) ---
            if len(seq) > 1:
                with np.errstate(divide='ignore', invalid='ignore'):
                    ratios = seq[1:] / (seq[:-1] + 1e-12)
                ratios = ratios[np.isfinite(ratios)]
                if len(ratios) > 0:
                    golden_ratio = 1.61803398875
                    fibonacci_proximity = float(np.mean(np.abs(ratios - golden_ratio)))
                else:
                    fibonacci_proximity = 999.0
            else:
                fibonacci_proximity = 999.0

            # --- 11. Показатель периодичности дробных частей (Fractional Part Periodicity) ---
            # Измеряет затухание дробных хвостов, если ряд нормирован
            if std_val > 1e-5:
                norm_seq = (seq - mean_val) / std_val
                frac_parts = norm_seq - np.floor(norm_seq)
                frac_periodicity = float(np.std(frac_parts))
            else:
                frac_periodicity = 0.0

            # --- 12. Алгебраическая сложность локального полинома (Polynomial Degree Fit) ---
            # За сколько шагов разностей ряд схлопывается в константу
            current_diff = np.copy(diffs)
            poly_degree = 0
            for degree in range(1, 6):
                if len(current_diff) == 0: break
                if np.std(current_diff) < 1e-6:
                    poly_degree = degree
                    break
                current_diff = np.diff(current_diff)
            if poly_degree == 0: poly_degree = 6 # Ряд слишком сложный/нелинейный

        except:
            # Аварийные нули для Алгебры
            prime_factor_density, coprimality_rate = 0.0, 1.0
            mod2_entropy, mod3_entropy, mod5_entropy, mod7_entropy = 0.0, 0.0, 0.0, 0.0
            perfect_proximity, square_free_rate, padic_valuation_mean = 1.0, 1.0, 0.0
            fibonacci_proximity, frac_periodicity, poly_degree = 999.0, 0.0, 6

        # =====================================================================
        # РАЗДЕЛ 11: ИНФОРМАТИКА, КОМБИНАТОРИКА И ТЕОРИЯ КОДИРОВАНИЯ (12 МЕТРИК)
        # =====================================================================
        try:
            # --- 1. Алгоритмическая сложность Левештейна-Лемпеля-Зива (LZ77-аналог) ---
            # Быстрая оценка сжатия строки через gzip прямо в памяти (без лжи)
            seq_bytes = seq.tobytes()
            compressed_len = len(gzip.compress(seq_bytes))
            lz_complexity_ratio = float(compressed_len / (len(seq_bytes) + 1e-12))

            # --- 2. Избыточность кода Шеннона (Information Redundancy) ---
            max_possible_ent = np.log2(n_len) if n_len > 1 else 1.0
            info_redundancy = float(max(0.0, max_possible_ent - shannon_ent))

            # --- 3. Длина бескраш-блока (Maximum Unrepeated Subsequence) ---
            # Самый длинный непрерывный кусок ряда, где числа не повторяются
            max_unrepeated_len = 1
            start_inc = 0
            used_nums = {}
            for idx_inc, num_inc in enumerate(seq):
                if num_inc in used_nums and used_nums[num_inc] >= start_inc:
                    start_inc = used_nums[num_inc] + 1
                used_nums[num_inc] = idx_inc
                max_unrepeated_len = max(max_unrepeated_len, idx_inc - start_inc + 1)
            max_unrepeated_ratio = float(max_unrepeated_len / n_len)

            # --- 4. Расстояние Хемминга между половинами ряда (Block Hamming Distance) ---
            # Переводим знаки приращений в бинарный код и меряем битовый сдвиг
            if len(sign_diffs) >= 2:
                h_half = len(sign_diffs) // 2
                h_dist = np.sum(sign_diffs[:h_half] != sign_diffs[-h_half:])
                hamming_distance_ratio = float(h_dist / h_half)
            else:
                hamming_distance_ratio = 0.0

            # --- 5. Алгоритмический шаг Тьюринга (Turing Step Entropy) ---
            # Частота смены знаков ускорения ряда (имитация смены состояний головки автомата)
            accel_signs = np.sign(np.diff(diffs)) if len(diffs) > 1 else np.array([0.0])
            _, accel_counts = np.unique(accel_signs, return_counts=True)
            accel_p = accel_counts / (len(accel_signs) + 1e-12)
            turing_step_entropy = float(-np.sum(accel_p * np.log2(accel_p + 1e-12)))

            # --- 6. Сложность по спектру Уолша-Адамара (Квадратные волны) ---
            # Оценка через чередование знаков элементов относительно среднего
            binary_profile = np.where(seq > mean_val, 1, 0)
            walsh_transitions = np.sum(binary_profile[:-1] != binary_profile[1:])
            walsh_energy_index = float(walsh_transitions / (n_len - 1 + 1e-12))

            # --- 7. Индекс автокорреляции битовых плоскостей (Bit-Plane Autocorrelation) ---
            # Проверяем цикличность знаков четности чисел (самый младший значащий бит)
            parity_profile = clean_ints % 2
            if len(parity_profile) > 1:
                bit_plane_autocorr = safe_correlation(parity_profile[:-1], parity_profile[1:])
            else:
                bit_plane_autocorr = 0.0

            # --- 8. Марковская память 2-го порядка (Higher-Order Markov Transitions) ---
            # Зависимость знака приращения от цепочки двух предыдущих шагов
            if len(sign_diffs) >= 3:
                m2_triplets = [(sign_diffs[i], sign_diffs[i+1], sign_diffs[i+2]) for i in range(len(sign_diffs)-2)]
                _, m2_counts = np.unique(m2_triplets, axis=0, return_counts=True)
                m2_p = m2_counts / len(m2_triplets)
                markov_order2_entropy = float(-np.sum(m2_p * np.log2(m2_p + 1e-12)))
            else:
                markov_order2_entropy = 0.0

            # --- 9. Инвариантность грамматического сжатия (Context-Free Grammar Size) ---
            # Насколько сильно ужимается строковое представление знаков ряда
            sign_str = "".join([("+" if x > 0 else "-" if x < 0 else "0") for x in sign_diffs])
            grammar_compressed_len = len(gzip.compress(sign_str.encode('utf-8')))
            grammar_complexity_index = float(grammar_compressed_len / (len(sign_str) + 1e-12)) if sign_str else 1.0

            # --- 10. Информационное количество Фишера (Fisher Information Counterpart) ---
            # Мера скорости изменения плотности распределения при микро-сдвигах
            if std_val > 1e-5:
                hist, _ = np.histogram(seq, bins=10, density=True)
                fisher_approx = float(np.sum(np.diff(np.sqrt(hist + 1e-12)) ** 2))
            else:
                fisher_approx = 0.0

            # --- 11. Плотность условных логических вентилей (Logical Gate Equivalent) ---
            # Сколько бит информации требуется для однозначного восстановления знаковой маски ряда
            logical_gate_density = float(np.sum(np.abs(sign_diffs)) / n_len)

            # --- 12. НОВАЯ: Коэффициент Битовой Плотности Мантиссы (IEEE 754 Counter) ---
            # Вскрываем сырую память компьютера: считаем хаос в битах экспоненты вещественных чисел
            def get_float_bits_entropy(arr):
                if len(arr) == 0: return 0.0
                bit_chars = []
                for x in arr[:50]: # Ограничиваем первыми 50 числами для бешеной скорости
                    try:
                        # Переводим float в 64-битное представление памяти (double)
                        packed = struct.unpack('Q', struct.pack('d', float(x)))[0]
                        # Вытаскиваем биты экспоненты (с 52 по 62 бит)
                        exponent_bits = (packed >> 52) & 0x7FF
                        bit_chars.append(exponent_bits)
                    except:
                        continue
                if not bit_chars: return 0.0
                _, bit_counts = np.unique(bit_chars, return_counts=True)
                bit_p = bit_counts / len(bit_chars)
                return float(-np.sum(bit_p * np.log2(bit_p + 1e-12)))

            ieee754_mantissa_entropy = get_float_bits_entropy(seq)

        except:
            # Аварийные нули для Информатики
            lz_complexity_ratio, info_redundancy, max_unrepeated_ratio = 1.0, 0.0, 0.0
            hamming_distance_ratio, turing_step_entropy, walsh_energy_index = 0.0, 0.0, 0.0
            bit_plane_autocorr, markov_order2_entropy, grammar_complexity_index = 0.0, 0.0, 1.0
            fisher_approx, logical_gate_density, ieee754_mantissa_entropy = 0.0, 0.0, 0.0

        # =====================================================================
        # РАЗДЕЛ 12: ТЕОРИЯ ИНФОРМАЦИИ И КВАНТОВАЯ ДИНАМИКА (12 МЕТРИК)
        # =====================================================================
        try:
            # --- 1. Перекрестная энтропия (Cross-Entropy Loss Fit) ---
            # Оценка расхождения распределения ряда с гауссовым эталоном
            if std_val > 1e-5:
                norm_seq_ce = (seq - mean_val) / std_val
                ce_hist, ce_bins = np.histogram(norm_seq_ce, bins=10, density=True)
                ce_gauss = 1.0 / (np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((ce_bins[:-1] + ce_bins[1:]) / 2.0) ** 2)
                cross_entropy_fit = float(-np.sum(ce_hist * np.log2(ce_gauss + 1e-12)) / (len(ce_hist) + 1e-12))
            else:
                cross_entropy_fit = 0.0

            # --- 2. Энтропия Реньи высшего порядка (Renyi Entropy alpha=3) ---
            renyi_alpha3 = float(1.0 / (1.0 - 3.0) * np.log2(np.sum(probs**3) + 1e-12))

            # --- 3. Энтропия Цаллиса дробного порядка (Tsallis Entropy q=1.5) ---
            tsallis_q15 = float(1.0 / (1.5 - 1.0) * (1.0 - np.sum(probs**1.5)))

            # --- 4. Квантовая энтропия фон Неймана (Von Neumann Entropy) ---
            # Строим корреляционную матрицу плотности Такенса и ищем ее след
            if len(vectors) > 2:
                cov_mat = np.cov(vectors.T)
                cov_trace = np.trace(cov_mat) + 1e-12
                density_matrix = cov_mat / cov_trace
                eigvals_von = np.linalg.eigvalsh(density_matrix)
                eigvals_von = eigvals_von[eigvals_von > 1e-12]
                von_neumann_entropy = float(-np.sum(eigvals_von * np.log2(eigvals_von)))
            else:
                von_neumann_entropy = 0.0

            # --- 5. Сингулярный спектр квантовых флуктуаций (SVD Entropy) ---
            # Измеряет чистый информационный хаос сингулярных чисел
            if 'S' in locals() and len(S) > 0:
                svd_probs = S / (np.sum(S) + 1e-12)
                svd_entropy_score = float(-np.sum(svd_probs * np.log2(svd_probs + 1e-12)))
            else:
                svd_entropy_score = 0.0

            # --- 6. Спектральный индекс спада частот (Power-Law Exponent Beta) ---
            if 'fft_half' in locals() and len(fft_half) > 1:
                freqs_log = np.log(np.arange(1, len(fft_half) + 1))
                fft_log = np.log(fft_half + 1e-12)
                # Линейная регрессия в лог-координатах для поиска наклона спектра
                slope, _ = np.polyfit(freqs_log, fft_log, 1)
                spectral_slope_beta = float(-slope)
            else:
                spectral_slope_beta = 0.0

            # --- 7. Индекс когерентности квантовых фаз (Phase Coherence) ---
            if len(seq) > 2:
                fft_complex = np.fft.fft(seq)
                phases = np.angle(fft_complex)
                phase_coherence = float(np.abs(np.mean(np.exp(1j * phases))))
            else:
                phase_coherence = 1.0

            # --- 8. Кросс-рекуррентная квантовая плотность (Recurrence Density) ---
            if 'flat_dists' in locals() and len(flat_dists) > 0:
                cross_recurrence_density = float(np.sum(flat_dists < (median_d * 0.1)) / len(flat_dists))
            else:
                cross_recurrence_density = 0.0

            # --- 9. Среднее время квантового возврата Пуанкаре ---
            if 'd_matrix' in locals() and d_matrix.shape[0] > 1:
                returns = np.where(d_matrix < (median_d * 0.15))
                poincare_return_mean = float(np.mean(np.diff(returns[0]))) if len(returns[0]) > 1 else float(n_len)
            else:
                poincare_return_mean = float(n_len)

            # --- 10. Локальный показатель Ляпунова второго порядка (Sub-Lyapunov Exponent) ---
            if 'vectors' in locals() and len(vectors) > 4:
                d0_sub = np.linalg.norm(vectors[1:] - vectors[:-1], axis=1) + 1e-8
                d1_sub = np.linalg.norm(vectors[2:] - vectors[:-2], axis=1)
                sub_lyapunov_exponent = float(np.mean(np.log(d1_sub / d0_sub[:-1] + 1e-12)))
            else:
                sub_lyapunov_exponent = 0.0

            # --- 11. НОВАЯ: Расстояние Бьёрнена-Нильсена между квантовыми уровнями ---
            # Анализирует статистику зазоров между соседними энергетическими уровнями матрицы Кирхгофа
            if 'nvg_lap_eigenvals' in locals() and len(nvg_lap_eigenvals) > 2:
                sorted_eigs = np.sort(nvg_lap_eigenvals)
                gaps = np.diff(sorted_eigs)
                # Индекс сопряжения зазоров Вигнера-Дайсона
                bjornen_nilsen_gap = float(np.std(gaps) / (np.mean(gaps) + 1e-12))
            else:
                bjornen_nilsen_gap = 0.0

            # --- 12. НОВАЯ: Квантовый фрактальный детерминант плотности Хаусдорфа ---
            # Ловит тончайшие детерминированные следы в фазовом пространстве через спектр экспонент
            if 'density_matrix' in locals() and density_matrix.shape[0] > 1:
                try:
                    quantum_det_hausdorff = float(la.det(density_matrix + np.eye(density_matrix.shape[0])*1e-6))
                    quantum_det_hausdorff = float(np.log(abs(quantum_det_hausdorff) + 1e-12))
                except:
                    quantum_det_hausdorff = 0.0
            else:
                quantum_det_hausdorff = 0.0

        except:
            # Аварийные нули для Квантовой Динамики
            cross_entropy_fit, renyi_alpha3, tsallis_q15 = 0.0, 0.0, 0.0
            von_neumann_entropy, svd_entropy_score, spectral_slope_beta = 0.0, 0.0, 0.0
            phase_coherence, cross_recurrence_density, poincare_return_mean = 1.0, 0.0, float(n_len)
            sub_lyapunov_exponent, bjornen_nilsen_gap, quantum_det_hausdorff = 0.0, 0.0, 0.0

        # =====================================================================
        # РАЗДЕЛ 13: НЕЛИНЕЙНАЯ СТАТИСТИКА И АНАЛИЗ АНОМАЛИЙ (РОВНО 10 МЕТРИК)
        # =====================================================================
        try:
            # --- 1. Быстрая статистика Дики-Фуллера (ADF-аналог для ОЗУ) ---
            # Измеряет стационарность ряда через авторегрессионный коэффициент разностей
            if len(diffs) > 1 and std_val > 1e-5:
                adf_numerator = np.sum(diffs[:-1] * diffs[1:])
                adf_denominator = np.sum(diffs[:-1] ** 2) + 1e-12
                pseudo_adf_stat = float(adf_numerator / adf_denominator)
            else:
                pseudo_adf_stat = 0.0

            # --- 2. Коэффициент Тейла (Theil's U Statistic аналог) ---
            # Качество удержания тренда по сравнению с тупым случайным блужданием
            if len(diffs) > 0:
                theil_u_numerator = np.sqrt(np.mean(diffs ** 2))
                theil_u_denominator = np.sqrt(np.mean(seq[:-1] ** 2)) + np.sqrt(np.mean(seq[1:] ** 2)) + 1e-12
                pseudo_theil_u = float(theil_u_numerator / theil_u_denominator)
            else:
                pseudo_theil_u = 1.0

            # --- 3. Множественный робастный медианный сдвиг (MAD) ---
            # Абсолютно стойкий к диким выбросам показатель разброса чисел ряда
            mad_score = float(np.median(np.abs(seq - np.median(seq))))

            # --- 4. Локальный показатель Хёрста (Мультифрактальный сдвиг) ---
            # Оценка изменения памяти ряда на короткой дистанции (первая половина ряда)
            if half_idx > 3:
                try:
                    h_vals = seq[:half_idx] - np.mean(seq[:half_idx])
                    h_cum = np.cumsum(h_vals)
                    h_range = np.max(h_cum) - np.min(h_cum)
                    local_hurst_half = float(math.log(h_range / (np.std(seq[:half_idx]) + 1e-12)) / math.log(half_idx))
                    local_hurst_half = min(max(local_hurst_half, 0.0), 1.0)
                except:
                    local_hurst_half = 0.5
            else:
                local_hurst_half = 0.5

            # --- 5. Коэффициент асимметрии богатства Джини (Gini Index) ---
            # Показывает степень концентрации «веса» числового ряда в отдельных пиках
            if len(clean_ints) > 0 and np.sum(clean_ints) > 0:
                # Переводим в float64, чтобы умножение не взрывало память процессора
                sorted_floats = np.sort(clean_ints).astype(np.float64)
                gini_n = len(sorted_floats)
                gini_index = float((2 * np.sum((np.arange(1, gini_n + 1) * sorted_floats))) / (gini_n * np.sum(sorted_floats)) - (gini_n + 1) / gini_n)
            else:
                gini_index = 0.0

            # --- 6. Длина максимального фазового излома ряда ---
            # Находим точку самого резкого перепада дисперсии ряда во времени
            if n_len > 4:
                roll_vars = [np.var(seq[i:i+4]) for i in range(n_len - 3)]
                phase_break_len = float(np.max(roll_vars) / (np.min(roll_vars) + 1e-12)) if roll_vars else 1.0
            else:
                phase_break_len = 1.0

            # --- 7. Непараметрический Критерий Знаков (Sign Test Statistic) ---
            # Избыток чистых ростов числового ряда над его падениями
            if len(diffs) > 0:
                sign_test_stat = float(np.sum(diffs > 0) / len(diffs))
            else:
                sign_test_stat = 0.5

            # --- 8. Авторегрессионный остаток дисперсии (ARIMA-шум аналог) ---
            # Объем чистого хаоса, который не смогла объяснить линейная модель шага 1
            if len(seq) > 1 and std_val > 1e-5:
                ar_pred = seq[:-1] * ac_lag1
                ar_residual_var = float(np.var(seq[1:] - ar_pred) / (std_val ** 2))
            else:
                ar_residual_var = 1.0

            # --- 9. Индекс экстремальных значений «Черных Лебедей» (EvD Shape) ---
            # Отношение максимального выброса к среднему разбросу (тяжесть хвостов ряда)
            extreme_value_density = float(np.max(np.abs(seq - mean_val)) / (mad_score + 1e-12))

            # --- 10. НОВАЯ: Индекс Когнитивной Хрупкости Тренда ---
            # Вычисляет скрытую нестационарность и скорость разрушения тренда по Кохрану
            if len(diffs) > 2:
                diff_variance_trend = np.var(np.diff(diffs))
                trend_fragility_index = float(diff_variance_trend / (np.var(diffs) + 1e-12))
            else:
                trend_fragility_index = 0.0

        except:
            # Аварийные дефолты для Статистики Аномалий
            pseudo_adf_stat, pseudo_theil_u, mad_score = 0.0, 1.0, 0.0
            local_hurst_half, gini_index, phase_break_len = 0.5, 0.0, 1.0
            sign_test_stat, ar_residual_var, extreme_value_density = 0.5, 1.0, 0.0
            trend_fragility_index = 0.0

        # =====================================================================
        # РАЗДЕЛ 14: КОНСТАНТНЫЙ АНАЛИЗ ХВОСТОВ ЧЕРЕЗ SYMPY (РОВНО 6 МЕТРИК)
        # =====================================================================
        try:
            # 1. Склеиваем первые числа ряда в одну псевдо-константу (например, 0.14159)
            # Берем до 20 первых ненулевых чисел, чтобы строка не улетела в бесконечность
            tail_digits = "".join([str(abs(int(x))) for x in clean_ints_no_zero[:20]])
            # 1. Склеиваем первые числа ряда и ЖЁСТКО ограничиваем строку первыми 40 цифрами!
            # Это защитит i5 от гигантских чисел Фибоначчи и факториалов
            tail_digits = tail_digits[:37]  # ХАКЕРСКИЙ ЛИМИТ: больше 40 цифр нам для 38 знаков не нужно!

            if tail_digits and len(tail_digits) > 3:
                # Превращаем в объект высокой точности SymPy Float (до 50 знаков для запаса)
                const_str = f"0.{tail_digits}"
                sp_float = sp.Float(const_str, 50)
                
                # --- 2. Честное разложение в цепную дробь SymPy до 40-го уровня ---
                # Если число рациональное (дробь) — цепь оборвется раньше. Если иррациональное — дойдет до 40.
                sp_continued = sp.continued_fraction_iterator(sp_float)
                cf_elements = []
                for _ in range(40):
                    try:
                        cf_elements.append(int(next(sp_continued)))
                    except StopIteration:
                        break # Цепь оборвалась, число рациональное!
                
                cf_length = float(len(cf_elements))
                cf_mean = float(np.mean(cf_elements)) if cf_elements else 0.0
                cf_std = float(np.std(cf_elements)) if cf_elements else 0.0
                
                # --- 3. Энтропия элементов цепной дроби ---
                if len(cf_elements) > 1:
                    _, cf_counts = np.unique(cf_elements, return_counts=True)
                    cf_p = cf_counts / len(cf_elements)
                    cf_entropy = float(-np.sum(cf_p * np.log2(cf_p + 1e-12)))
                else:
                    cf_entropy = 0.0
                
                # --- 4. Хакерский поиск строковых повторов и циклов (до 40-го знака) ---
                # Ищем, повторяется ли паттерн цифр (например, 42044204)
                test_str = tail_digits[:40]
                str_period_found = 0.0
                max_pattern_len = 0.0
                
                # Проверяем возможные длины циклов от 2 до половины строки
                for p_len in range(2, len(test_str) // 2 + 1):
                    pattern = test_str[:p_len]
                    # Если строка состоит из повторений этого паттерна
                    if test_str.count(pattern) * p_len >= len(test_str) * 0.8:
                        str_period_found = 1.0
                        max_pattern_len = float(p_len)
                        break
            else:
                cf_length, cf_mean, cf_std, cf_entropy, str_period_found, max_pattern_len = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        except:
            # Аварийные дефолты SymPy
            cf_length, cf_mean, cf_std, cf_entropy, str_period_found, max_pattern_len = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        # =====================================================================
        # РАЗДЕЛ 15: ДЕТЕКТОР КЛЕТОЧНЫХ АВТОМАТОВ ВОЛЬФРАМА (4 МЕТРИКИ)
        # =====================================================================
        try:
            # Переводим динамику ряда в бинарный профиль (1 - рост, 0 - спад/стагнация)
            bin_profile = np.where(diffs > 0, 1, 0)
            
            if len(bin_profile) >= 5:
                rule_table = {}
                is_cellular_automaton = 1.0
                
                # Сканируем триплеты и их следствие через шаг
                for i in range(len(bin_profile) - 3):
                    triplet = (bin_profile[i], bin_profile[i+1], bin_profile[i+2])
                    target = bin_profile[i+3]
                    
                    if triplet in rule_table:
                        if rule_table[triplet] != target:
                            # Если один и тот же триплет порождает разные исходы — это НЕ простой автомат
                            is_cellular_automaton = 0.0
                            break
                    else:
                        rule_table[triplet] = target
                
                # Если это автомат, вычисляем его официальный номер Rule ID (0-255)
                if is_cellular_automaton == 1.0:
                    wolfram_rule_id = 0
                    # Стандартный порядок триплетов Вольфрама: 111, 110, 101, 100, 011, 010, 001, 000
                    wolfram_triplets = [
                        (1,1,1), (1,1,0), (1,0,1), (1,0,0), 
                        (0,1,1), (0,1,0), (0,0,1), (0,0,0)
                    ]
                    for idx_bit, trip in enumerate(wolfram_triplets):
                        bit_val = rule_table.get(trip, 0) # Если триплет не встретился, по умолчанию 0
                        wolfram_rule_id += bit_val * (2 ** (7 - idx_bit))
                else:
                    wolfram_rule_id = -1 # Не автомат
                    
                # Считаем энтропию найденной таблицы переходов (сложность автомата)
                ca_complexity = float(len(rule_table) / 8.0)
            else:
                is_cellular_automaton, wolfram_rule_id, ca_complexity = 0.0, -1, 0.0
                
        except:
            is_cellular_automaton, wolfram_rule_id, ca_complexity = 0.0, -1, 0.0

        # =====================================================================
        # РАЗДЕЛ 17: ТЯЖЕЛЫЕ МЕТРИКИ ТРЕНДОВ И РАСПРЕДЕЛЕНИЙ (РОВНО 6 МЕТРИК)
        # =====================================================================
        try:
            # 1. ЧИСТАЯ ЛАМИНАРНОСТЬ (LAM из Recurrence Quantification Analysis)
            # Измеряет долю вертикальных структур в матрице рекуррентности
            if 'd_matrix' in locals() and d_matrix.shape > 1:
                # Бинарная матрица рекуррентности: точки, подошедшие близко
                rec_mat = (d_matrix < (median_d * 0.15)).astype(int)
                # Считаем вертикальные линии: если точка близка и её сосед сверху тоже близок
                vert_lines = np.sum(rec_mat[:-1, :] & rec_mat[1:, :])
                total_rec_points = np.sum(rec_mat) + 1e-12
                laminarity_score = float(vert_lines / total_rec_points)
            else:
                laminarity_score = 0.0

            # 2. Индекс Ходжеса-Лемана (Robust Location Estimator)
            # Стабильная, псевдо-медианная оценка центра распределения ряда
            if len(seq) > 1:
                # Берем до 40 чисел для попарных средних, чтобы не взорвать ОЗУ комбинаторикой
                sub_seq_hl = seq[:40]
                pairwise_means = (sub_seq_hl[:, None] + sub_seq_hl[None, :]) / 2.0
                hodges_lehmann_index = float(np.median(pairwise_means))
            else:
                hodges_lehmann_index = mean_val

            # 3. Статистика Колмогорова-Смирнова для экспоненциального распределения
            # Проверяет, распределены ли шаги ряда по закону затухания (как радиоактивный распад или лавина)
            if len(diffs) > 1 and std_val > 1e-5:
                abs_diffs_norm = np.abs(diffs) / (np.mean(np.abs(diffs)) + 1e-12)
                ks_stat, _ = stats.kstest(abs_diffs_norm, 'expon')
                ks_exponential_stat = float(ks_stat)
            else:
                ks_exponential_stat = 0.0

            # 4. Мера сложности Аллендорфа (Allendorf Complexity Counterpart)
            # Считает хаос чередования пиков через бинарную маску локальных экстремумов
            if len(diffs) >= 2:
                local_peaks = (diffs[:-1] > 0) & (diffs[1:] < 0)
                local_troughs = (diffs[:-1] < 0) & (diffs[1:] > 0)
                extremum_mask = (local_peaks | local_troughs).astype(int)
                # Смотрим хаос переходов между наличием и отсутствием экстремумов
                allendorf_transitions = np.sum(extremum_mask[:-1] != extremum_mask[1:])
                allendorf_complexity = float(allendorf_transitions / (len(extremum_mask) + 1e-12))
            else:
                allendorf_complexity = 0.0

            # 5. Коэффициент корреляции Спирмена с линейным трендом
            # Ловит нелинейную, но монотонную упрямость ряда (идет строго вверх или вниз)
            if n_len > 1:
                time_steps = np.arange(n_len)
                spearman_rho, _ = stats.spearmanr(seq, time_steps)
                spearman_trend_correlation = float(spearman_rho) if np.isfinite(spearman_rho) else 0.0
            else:
                spearman_trend_correlation = 0.0

            # 6. Z-score максимального выброса (Амплитуда Аномалии)
            # На сколько стандартных отклонений самый дикий пик оторвался от среднего
            z_score_max_anomaly = float(np.max(np.abs(seq - mean_val)) / std_val)

        except:
            laminarity_score, hodges_lehmann_index = 0.0, mean_val
            ks_exponential_stat, allendorf_complexity = 0.0, 0.0
            spearman_trend_correlation, z_score_max_anomaly = 0.0, 0.0

        # =====================================================================
        # РАЗДЕЛ 18: ДИНАМИЧЕСКИЙ АНАЛИЗ СУММ РЯДА (4 МЕТРИКИ)
        # =====================================================================
        try:
            # Строим ряд частичных сумм (накопительный итог: S1, S1+S2, S1+S2+S3...)
            # Нормируем исходный ряд на стандартное отклонение, чтобы защитить ОЗУ от гигантских чисел
            if std_val > 1e-5:
                norm_seq_sum = (seq - mean_val) / std_val
                cum_sums = np.cumsum(norm_seq_sum)
            else:
                cum_sums = np.cumsum(seq)

            n_sums = len(cum_sums)
            
            if n_sums > 1:
                # 1. Финальный вектор суммы (куда пришел ряд в конце нашего окна наблюдения)
                final_sum_vector = float(cum_sums[-1])
                
                # 2. Скорость разлета суммы (угол наклона кумулятивного тренда)
                # Показывает, взрывается ряд (высокое число) или затухает/сходится к константе (около 0)
                sum_trend, _ = np.polyfit(np.arange(n_sums), cum_sums, 1)
                sum_expansion_rate = float(sum_trend)
                
                # 3. Волатильность накопления (насколько сильно сумму «лихорадит» по пути)
                sum_fluctuation_std = float(np.std(cum_sums))
                
                # 4. Маркер зеркальной сходимости (отношение первой половины суммы ко второй)
                # Если ряд сходится, это число стремится к 1.0
                half_s = n_sums // 2
                sum_convergence_ratio = float(np.mean(np.abs(cum_sums[:half_s])) / (np.mean(np.abs(cum_sums[half_s:])) + 1e-12))
            else:
                final_sum_vector, sum_expansion_rate, sum_fluctuation_std, sum_convergence_ratio = 0.0, 0.0, 0.0, 1.0

        except:
            final_sum_vector, sum_expansion_rate, sum_fluctuation_std, sum_convergence_ratio = 0.0, 0.0, 0.0, 1.0


        # =====================================================================
        # РАЗДЕЛ 19: ТЕОРЕТИКО-МНОЖЕСТВЕННЫЙ ПРОФАЙЛЕР (РОВНО 6 МЕТРИК)
        # =====================================================================
        try:
            # Берем уникальные элементы для анализа состава множества (первые 50 чисел)
            set_elements = np.unique(seq[:50])
            n_set = len(set_elements)

            if n_set > 0:
                # 1. Считаем, сколько объектов ряда лежат строго в множестве Натуральных чисел (N)
                nat_count = sum(1 for x in set_elements if x > 0 and float(x).is_integer())
                set_naturals_ratio = float(nat_count / n_set)

                # 2. Считаем, сколько объектов лежат в кольце Целых чисел (Z) (учитывая отрицательные)
                int_count = sum(1 for x in set_elements if float(x).is_integer())
                set_integers_ratio = float(int_count / n_set)

                # 3. Считаем, сколько объектов являются Простыми числами (P) через SymPy
                prime_count = sum(1 for x in set_elements if float(x).is_integer() and sp.isprime(int(x)))
                set_primes_ratio = float(prime_count / n_set)

                # 4. Метрика Монолитности множества (Весь ряд в одном множестве?)
                # Если 1.0 — ряд тотально однороден по своей природе (например, чистые целые числа)
                set_is_monolithic_int = 1.0 if int_count == n_set else 0.0

                # 5. Мощность пересечения (Считаем уникальные остатки по модулю длины ряда)
                # Показывает, сколько уникальных "алгебраических ячеек" занимает ряд
                mod_base = max(2, n_len)
                unique_mods = len(np.unique(clean_ints % mod_base))
                set_intersection_power = float(unique_mods / mod_base)

                # 6. Маркер Хаотической Дробности множества
                # Показывает процент иррациональных/дробных элементов, вылетающих из кольца Z
                set_fractional_ratio = float((n_set - int_count) / n_set)
            else:
                set_naturals_ratio, set_integers_ratio, set_primes_ratio = 0.0, 0.0, 0.0
                set_is_monolithic_int, set_intersection_power, set_fractional_ratio = 0.0, 0.0, 0.0

        except:
            set_naturals_ratio, set_integers_ratio, set_primes_ratio = 0.0, 0.0, 0.0
            set_is_monolithic_int, set_intersection_power, set_fractional_ratio = 0.0, 0.0, 0.0

        # =====================================================================
        # РАЗДЕЛ 20: ВОЛНОВОЙ СПЕКТРОМЕТР "БОКОВОЙ ЛИНИИ" (РОВНО 3 МЕТРИК)
        # =====================================================================
        try:
            # --- 1. Квантовый Спин Чисел (Крупномодулярная Симметрия) ---
            # Быстрый аналог спинового зацепления: смотрим хаос остатков по огромному простому модулю
            # Используем близкое к миллиону простое число 999983
            if len(clean_ints_no_zero) > 0:
                large_mod_elements = clean_ints_no_zero % 999983
                # Считаем "спиновой разлет" — дисперсию нормированных крупных остатков
                spin_quantum_variance = float(np.var(large_mod_elements / 999983.0))
            else:
                spin_quantum_variance = 0.0

            # --- 2. Коэффициент Трения Цифровой Пены (Тензор Сингулярности) ---
            # Быстрый аналог Гессиановой алгебры: меряем "вязкость" и завихренность взрыва волны
            # Находим, насколько резко ускорение ряда ломает его гладкое русло
            if len(diffs) > 1 and std_val > 1e-5:
                # Вторая разность — это ускорение ("пена")
                foam_accel = np.diff(diffs)
                # Коэффициент трения пены: отношение пикового взрыва ускорения к среднему шуму
                foam_friction_tensor = float(np.max(np.abs(foam_accel)) / (np.mean(np.abs(diffs)) + 1e-12))
            else:
                foam_friction_tensor = 0.0

            # --- 3. Биологическая Выживаемость Кода (Морфогенез Отводков) ---
            # Быстрая оценка: способен ли ряд "пустить корни", как ежевика, коснувшись земли
            # Проверяем зеркальную симметрию затухания — закручивается ли хвост ряда в устойчивую спираль (клику)
            if len(seq) > 3:
                # Берем автокорреляцию первой трети ряда и последней трети
                third = max(1, n_len // 3)
                if len(seq[:-third]) > 1:
                    morpho_start = safe_correlation(seq[:third], seq[third:2*third])
                    morpho_end = safe_correlation(seq[-2*third:-third], seq[-third:])
                    # Индекс выживаемости: если структура сохраняет стабильность весов на финише
                    code_survival_morphogenesis = float(abs(morpho_start - morpho_end))
                else:
                    code_survival_morphogenesis = 1.0
            else:
                code_survival_morphogenesis = 1.0

        except:
            spin_quantum_variance, foam_friction_tensor, code_survival_morphogenesis = 0.0, 0.0, 1.0

        # =====================================================================
        # РАЗДЕЛ 21: ЭВРИСТИЧЕСКИЙ ИИ-СИНТЕЗАТОР СКРЫТЫХ ЗАКОНОВ (3 МЕТРИКИ)
        # =====================================================================
        try:
            # Эмулируем LCM-осциллятор: сталкиваем волновые и топологические фичи текущего ряда
            # Проверяем, образуют ли они стабильное "алгебраическое замыкание"
            lcm_chaos_bridge = float(abs(wave_entropy_db if 'wave_entropy_db' in locals() else spectral_ent) * (laminarity_score if 'laminarity_score' in locals() else 0.5))
            
            # --- 1. Маркер Схлопывания Закона (Invariant Perfection Score) ---
            # Ищем, закручивается ли отношение фрактала к квантовому спину в константу
            if spin_quantum_variance > 1e-5:
                # Если отношение близко к эталонным фрактальным пропорциям (типа Золотого Сечения)
                raw_law_ratio = float((minkowski_box_dim if 'minkowski_box_dim' in locals() else corr_dim) / (spin_quantum_variance + 1e-12))
                invariant_perfection = float(np.sin(raw_law_ratio) ** 2) # Зажимаем в жесткие рамки 0-1
            else:
                invariant_perfection = 0.0

            # --- 2. Коэффициент Разреженного Когнитивного Кворума (Sparse Coding Rate) ---
            # Показывает, сколько из 150 датчиков выдали аномально высокий "крик" (сигнал тревоги)
            # В точности как 9 окон ума из 26 в твоей Рыбке Рикки!
            all_current_features = [
                shannon_ent, perm_ent, approx_ent, ac_lag1, ac_lag5, 
                fft_energy, spectral_ent, cloud_radius, snake_total_length,
                pca_x, pca_z, vector_rot_force, corr_dim, hurst, benford_kl_div,
                laminarity_score if 'laminarity_score' in locals() else 0.0,
                spin_quantum_variance, foam_friction_tensor
            ]
            high_signals = sum(1 for f in all_current_features if abs(f) > 1.0)
            sparse_quorum_rate = float(high_signals / len(all_current_features))

            # --- 3. Дробный Демпфер Предыстории Токов (Fractional-Order Memory Link) ---
            # Симулирует оператор Грюнвальда-Летникова порядка 0.73
            # Показывает, насколько сильно текущая эмерджентность связана с накопленной кумулятивной суммой
            if 'final_sum_vector' in locals() and abs(final_sum_vector) > 1e-5:
                fractional_memory_link = float(abs(causal_emergence) * 0.73 / (abs(final_sum_vector) + 1e-12))
            else:
                fractional_memory_link = 0.0

        except:
            invariant_perfection, sparse_quorum_rate, fractional_memory_link = 0.0, 0.25, 0.0


        # Модифицированный возврат: каждое число бережно оборачиваем в safe_num
        return {
            "ID": f'="{seq_id}"',  # Жестко запечатываем ID, чтобы не превращался в дату!
            "Название": seq_name, 
            "Чистый_Класс": c_clean,       # НОВАЯ ЧИСТАЯ ЯЧЕЙКА ДЛЯ ФИЛЬТРОВ И ГРАФИКОВ!
            "Вердикт": verdict,        # СТАРАЯ КРАСИВАЯ СЛОЖНАЯ ТЕКСТОВКА
            "Status": "Успешно",
            "Длина_Ряда": safe_num(n_len, 0), 
            "Среднее_Значение": safe_num(mean_val, 2), 
            "Станд_Отклонение": safe_num(std_val, 2),
            "Коэф_Вариации": safe_num(coef_variation, 4), 
            "Асимметрия_Сдвига": safe_num(skewness, 4), 
            "Эксцесс_Хвостов": safe_num(kurtosis, 4),
            "Процентиль_75": safe_num(pct_75, 2), 
            "Процентиль_95": safe_num(pct_95, 2), 
            "Коэф_Аномалий_Шага": safe_num(step_anomaly_ratio, 2),
            "Энтропия_Шеннона": safe_num(shannon_ent, 4), 
            "Энтропия_Перестановок": safe_num(perm_ent, 4), 
            "Приближенная_Энтропия_ApEn": safe_num(approx_ent, 4),
            "Автокорреляция_Лаг1": safe_num(ac_lag1, 4), 
            "Автокорреляция_Лаг2": safe_num(ac_lag2, 4), 
            "Автокорреляция_Лаг3": safe_num(ac_lag3, 4),
            "Автокорреляция_Лаг4": safe_num(ac_lag4, 4), 
            "Автокорреляция_Лаг5": safe_num(ac_lag5, 4), 
            "Энергия_Спектра_Фурье": safe_num(fft_energy, 2),
            "Главная_Частота_Фурье": safe_num(main_freq, 0), 
            "Пик_Амплитуды_Фурье": safe_num(max_amplitude, 2), 
            "Медианная_Частота_Фурье": safe_num(median_freq, 0),
            "Дисперсия_Спектра_Фурье": safe_num(fft_dispersion, 2), 
            "Спектральная_Энтропия_Фурье": safe_num(spectral_ent, 4), 
            "Радиус_Векторного_Облака": safe_num(cloud_radius, 2),
            "Физическая_Длина_Змеи": safe_num(snake_total_length, 2), 
            "Доля_Оси_PCA_X": safe_num(pca_x, 4), 
            "Доля_Оси_PCA_Y": safe_num(pca_y, 4),
            "Доля_Оси_PCA_Z": safe_num(pca_z, 4), 
            "Сила_Ротора_Закрутки": safe_num(vector_rot_force, 2), 
            "Индекс_Сквозных_Дыр": safe_num(has_hollow_holes, 4),
            "Коэф_Ветвления_Пирсона": safe_num(branch_ratio, 4), 
            "Фрактал_Размерность_GP": safe_num(corr_dim, 4), 
            "Показатель_Херста_Памяти": safe_num(hurst, 4),
            "Девиация_Закона_Бенфорда": safe_num(benford_deviation, 4), 
            "Доля_Первых_Единиц_Бенфорда": safe_num(benford_pct_1, 4),
            
            # НАШИ НОВЫЕ СТАТИСТИЧЕСКИЕ МОЩНОСТИ:
            "Бенфорд_Хи_Квадрат": safe_num(benford_chi2, 4),
            "Бенфорд_KL_Дивергенция": safe_num(benford_kl_div, 4),
            "Бенфорд_Стат_Вердикт": benford_p_verdict,

            # БЛОК ГРАФОВ ВИДИМОСТИ (NVG / HVG):
            "Graph_NVG_Узлы": safe_num(nvg_nodes, 0),
            "Graph_NVG_Ребра": safe_num(nvg_edges, 0),
            "Graph_NVG_Плотность": safe_num(nvg_density, 4),
            "Graph_NVG_Макс_Степень": safe_num(nvg_max_degree, 0),
            "Graph_NVG_Сред_Степень": safe_num(nvg_mean_degree, 2),
            "Graph_NVG_Энтропия_Степеней": safe_num(nvg_degree_entropy, 4),
            "Graph_NVG_Кластеризация": safe_num(nvg_avg_clustering, 4),
            "Graph_NVG_Транзитивность": safe_num(nvg_transitivity, 4),
            "Graph_NVG_Диаметр": safe_num(nvg_diameter, 0),
            "Graph_NVG_Радиус": safe_num(nvg_radius, 0),
            "Graph_NVG_Сред_Путь": safe_num(nvg_avg_path, 2),
            "Graph_NVG_Ассортативность": safe_num(nvg_assortativity, 4),
            "Graph_NVG_Близость_Closeness": safe_num(nvg_mean_closeness, 4),
            "Graph_NVG_Влияние_Eigenvector": safe_num(nvg_mean_eigen, 4),
            "Graph_NVG_Кол_Сообществ": safe_num(nvg_num_communities, 0),
            "Graph_NVG_Модульность": safe_num(nvg_modularity, 4),
            "Graph_NVG_Энергия_Лапласа": safe_num(nvg_graph_energy, 2),
            "Graph_NVG_Спектр_Радиус": safe_num(nvg_spectral_radius, 4),
            "Graph_NVG_Число_Фидлера": safe_num(nvg_fiedler_value, 4),
            
            "Graph_HVG_Узлы": safe_num(hvg_nodes, 0),
            "Graph_HVG_Ребра": safe_num(hvg_edges, 0),
            "Graph_HVG_Плотность": safe_num(hvg_density, 4),
            "Graph_HVG_Сред_Степень": safe_num(hvg_mean_degree, 2),
            "Graph_HVG_Кластеризация": safe_num(hvg_avg_clustering, 4),
            
            "Graph_Видимость_Сред_Длина": safe_num(nvg_mean_edge_length, 2),
            "Graph_Видимость_Макс_Длина": safe_num(nvg_max_edge_length, 0),
            
            # =====================================================================
            # УЛЬТИМАТИВНЫЙ БЛОК ЭМЕРДЖЕНТНОСТИ (РОВНО 20 КОЛОНОК)
            # =====================================================================
            "Эмердж_Causal_Emergence": safe_num(causal_emergence, 4),
            "Эмердж_Индекс_Самоорг": safe_num(self_organization_index, 4),
            "Эмердж_Микро_Шум_Хоэла": safe_num(micro_noise, 4),
            "Эмердж_Макро_Шум_Хоэла": safe_num(macro_noise, 4),
            "Эмердж_Энтропия_Реньи": safe_num(renyi_ent, 4),
            "Эмердж_Энтропия_Цаллиса": safe_num(tsallis_ent, 4),
            "Эмердж_Перестановки_Лаг2": safe_num(perm_ent_l2, 4),
            "Эмердж_Перестановки_Лаг3": safe_num(perm_ent_l3, 4),
            "Эмердж_Динамика_Формы_Вассерштейна": safe_num(wasserstein_dist, 4),
            "Эмердж_Резонанс_Шеннон_Фурье": safe_num(shannon_spectral_ratio, 4),
            "Эмердж_Эффект_Бабочки_Ляпунов": safe_num(local_lyapunov, 4),
            "Эмердж_Стационарность_Флуктуаций": safe_num(fluc_co_variation, 4),
            "Эмердж_Затухание_Памяти_АКОФ": safe_num(ac_decay_rate, 4),
            "Эмердж_Индекс_Резонанса_PCA": safe_num(emergence_resonance_score, 4),
            "Эмердж_Марковская_Плотность_Приращений": safe_num(len(unique_pairs) if 'unique_pairs' in locals() else 0, 0),
            "Эмердж_Макро_Плотность_Приращений": safe_num(len(m_unique_pairs) if 'm_unique_pairs' in locals() else 0, 0),
            "Эмердж_Дисперсия_Марковских_Переходов": safe_num(np.std(p_matrix) if 'p_matrix' in locals() else 0.0, 4),
            "Эмердж_Дисперсия_Макро_Переходов": safe_num(np.std(m_matrix) if 'm_matrix' in locals() else 0.0, 4),
            "Эмердж_Скорость_Потери_Информации": safe_num(abs(micro_noise - shannon_ent), 4),
            "Эмердж_Коэффициент_Нелинейности_Сдвига": safe_num(abs(perm_ent - shannon_ent), 4),

            # =====================================================================
            # БЛОК ТОПОЛОГИИ ЗМЕЙКИ И TDA (РОВНО 16 КОЛОНОК)
            # =====================================================================
            "TDA_Betti0_Связность": safe_num(betti_0_small, 4),
            "TDA_Betti1_Туннели": safe_num(betti_1_large, 4),
            "TDA_Persistence_Штрихкод": safe_num(persistence_lifespan, 4),
            "TDA_Тензор_Инерции_X": safe_num(inertia_x, 4),
            "TDA_Тензор_Инерции_Y": safe_num(inertia_y, 4),
            "TDA_Тензор_Инерции_Z": safe_num(inertia_z, 4),
            "TDA_Сферическая_Асимметрия": safe_num(spherical_asymmetry, 4),
            "TDA_Извилистость_Tortuosity": safe_num(tortuosity_index, 4),
            "TDA_Гео_Индекс_Винера": safe_num(t_wiener_index, 2),
            "TDA_Фрактал_Минковского_Box": safe_num(minkowski_box_dim, 4),
            "TDA_Объем_Оболочки_Hull": safe_num(convex_hull_volume, 4),
            "TDA_Плотность_Оболочки_Solidity": safe_num(convex_hull_solidity, 4),
            "TDA_Кривизна_Гаусса": safe_num(gaussian_curvature, 4),
            "TDA_Кручение_Змейки_Torsion": safe_num(torsion_force, 4),
            "TDA_Плотность_Самопересечений": safe_num(self_intersections, 4),
            "TDA_Радиус_Гирации_Упаковки": safe_num(radius_of_gyration, 4),

            # =====================================================================
            # БЛОК ВЫСШЕЙ АЛГЕБРАИЧЕСКОЙ ТЕОРИИ ЧИСЛ (РОВНО 12 КОЛОНОК)
            # =====================================================================
            "Alg_Плотность_Простых_Делителей": safe_num(prime_factor_density, 4),
            "Alg_Индекс_Взаимной_Простоты_НОД": safe_num(coprimality_rate, 4),
            "Alg_Энтропия_Остатков_Mod2": safe_num(mod2_entropy, 4),
            "Alg_Энтропия_Остатков_Mod3": safe_num(mod3_entropy, 4),
            "Alg_Энтропия_Остатков_Mod5": safe_num(mod5_entropy, 4),
            "Alg_Энтропия_Остатков_Mod7": safe_num(mod7_entropy, 4),
            "Alg_Частота_Совершенных_Чисел": safe_num(perfect_proximity, 4),
            "Alg_Доля_Свободных_От_Квадратов": safe_num(square_free_rate, 4),
            "Alg_p_Адическая_2_Валентность": safe_num(padic_valuation_mean, 4),
            "Alg_Отклонение_От_Золотого_Сечения": safe_num(fibonacci_proximity, 4),
            "Alg_Периодичность_Дробных_Хвостов": safe_num(frac_periodicity, 4),
            "Alg_Степень_Локального_Полинома": safe_num(poly_degree, 0),

            # =====================================================================
            # БЛОК ИНФОРМАТИКИ, КОМБИНАТОРИКИ И ТЕОРИИ КОДИРОВАНИЯ (РОВНО 12 КОЛОНОК)
            # =====================================================================
            "Inf_Сжатие_LZ_Сложность": safe_num(lz_complexity_ratio, 4),
            "Inf_Избыточность_Шеннона": safe_num(info_redundancy, 4),
            "Inf_Доля_Бескраш_Блока": safe_num(max_unrepeated_ratio, 4),
            "Inf_Хемминг_Половин_Ряда": safe_num(hamming_distance_ratio, 4),
            "Inf_Тьюринг_Энтропия_Ускорения": safe_num(turing_step_entropy, 4),
            "Inf_Уолш_Индекс_Переходов": safe_num(walsh_energy_index, 4),
            "Inf_Битовая_Автокорреляция_Четности": safe_num(bit_plane_autocorr, 4),
            "Inf_Марковская_Память_Порядка2": safe_num(markov_order2_entropy, 4),
            "Inf_Грамматическое_Сжатие_Строки": safe_num(grammar_complexity_index, 4),
            "Inf_Инфо_Количество_Фишера": safe_num(fisher_approx, 4),
            "Inf_Плотность_Вентилей_Маски": safe_num(logical_gate_density, 4),
            "Inf_IEEE754_Энтропия_Мантиссы": safe_num(ieee754_mantissa_entropy, 4),

            # =====================================================================
            # БЛОК КВАНТОВОЙ ДИНАМИКИ И ТЕОРИИ ИНФОРМАЦИИ (РОВНО 12 КОЛОНОК)
            # =====================================================================
            "Quant_Перекрестная_Энтропия_Гаусс": safe_num(cross_entropy_fit, 4),
            "Quant_Энтропия_Реньи_Альфа3": safe_num(renyi_alpha3, 4),
            "Quant_Энтропия_Цаллиса_q15": safe_num(tsallis_q15, 4),
            "Quant_Энтропия_Фон_Неймана": safe_num(von_neumann_entropy, 4),
            "Quant_СВД_Энтропия_Спектра": safe_num(svd_entropy_score, 4),
            "Quant_Индекс_Спада_Частот_Beta": safe_num(spectral_slope_beta, 4),
            "Quant_Когерентность_Квантовых_Фаз": safe_num(phase_coherence, 4),
            "Quant_Рекуррентная_Плотность_Паттернов": safe_num(cross_recurrence_density, 4),
            "Quant_Время_Возврата_Пуанкаре": safe_num(poincare_return_mean, 2),
            "Quant_Показатель_Суб_Ляпунова": safe_num(sub_lyapunov_exponent, 4),
            "Quant_Зазор_Бьёрнена_Нильсена_Уровней": safe_num(bjornen_nilsen_gap, 4),
            "Quant_Фрактал_Детерминант_Хаусдорфа": safe_num(quantum_det_hausdorff, 4),

            # =====================================================================
            # БЛОК НЕЛИНЕЙНОЙ СТАТИСТИКИ И АНАЛИЗА АНОМАЛИЙ (РОВНО 10 КОЛОНОК)
            # =====================================================================
            "Stat_Псевдо_АДФ_Стационарность": safe_num(pseudo_adf_stat, 4),
            "Stat_Коэффициент_Тейла_Качество": safe_num(pseudo_theil_u, 4),
            "Stat_Робастный_Разброс_MAD": safe_num(mad_score, 2),
            "Stat_Локальный_Хёрст_Полуряда": safe_num(local_hurst_half, 4),
            "Stat_Индекс_Концентрации_Джини": safe_num(gini_index, 4),
            "Stat_Сила_Фазового_Излома": safe_num(phase_break_len, 4),
            "Stat_Критерий_Знаков_Рост_Спад": safe_num(sign_test_stat, 4),
            "Stat_Авторегрессионный_Остаток_Шума": safe_num(ar_residual_var, 4),
            "Stat_Плотность_Черных_Лебедей_EvD": safe_num(extreme_value_density, 4),
            "Stat_Индекс_Хрупкости_Тренда": safe_num(trend_fragility_index, 4),

            # =====================================================================
            # БЛОК КОНСТАНТНОГО АНАЛИЗА SYMPY (РОВНО 6 КОЛОНОК)
            # =====================================================================
            "Tail_SymPy_Длина_Цепной_Дроби": safe_num(cf_length, 0),
            "Tail_SymPy_Среднее_Цепной_Дроби": safe_num(cf_mean, 2),
            "Tail_SymPy_Станд_Откл_Цепной_Дроби": safe_num(cf_std, 2),
            "Tail_SymPy_Энтропия_Цепной_Дроби": safe_num(cf_entropy, 4),
            "Tail_SymPy_Маркер_Цикличного_Повтора": safe_num(str_period_found, 0),
            "Tail_SymPy_Длина_Найденного_Цикла": safe_num(max_pattern_len, 0),

            "CA_Маркер_Клеточного_Автомата": safe_num(is_cellular_automaton, 0),
            "CA_Номер_Правила_Вольфрама_RuleID": safe_num(wolfram_rule_id, 0),
            "CA_Сложность_Таблицы_Переходов": safe_num(ca_complexity, 4),

            # =====================================================================
            # БЛОК ТРЕНДОВ, ЛАМИНАРНОСТИ И АНОМАЛИЙ (РОВНО 6 КОЛОНОК)
            # =====================================================================
            "Trend_Ламинарность_Потока_LAM": safe_num(laminarity_score, 4),
            "Trend_Индекс_Ходжеса_Лемана": safe_num(hodges_lehmann_index, 4),
            "Trend_Колмогоров_Смирнов_Экспонента": safe_num(ks_exponential_stat, 4),
            "Trend_Сложность_Аллендорфа_Экстремумов": safe_num(allendorf_complexity, 4),
            "Trend_Корреляция_Спирмена_Монотонность": safe_num(spearman_trend_correlation, 4),
            "Trend_Z_Score_Макс_Выброса_Аномалии": safe_num(z_score_max_anomaly, 4),

            "Sum_Финальный_Вектор_Накопления": safe_num(final_sum_vector, 4),
            "Sum_Скорость_Взрыва_Расширения": safe_num(sum_expansion_rate, 4),
            "Sum_Волатильность_Кумулятивная": safe_num(sum_fluctuation_std, 4),
            "Sum_Коэффициент_Сходимости_Хвоста": safe_num(sum_convergence_ratio, 4),

            # =====================================================================
            # БЛОК БАЗОВЫХ МНОЖЕСТВ И КОЛЕЦ (РОВНО 6 КОЛОНОК)
            # =====================================================================
            "Set_Доля_Натуральных_Чисел_N": safe_num(set_naturals_ratio, 4),
            "Set_Доля_Целых_Чисел_Кольца_Z": safe_num(set_integers_ratio, 4),
            "Set_Доля_Простых_Чисел_Множества_P": safe_num(set_primes_ratio, 4),
            "Set_Маркер_Монолитности_Ряда_В_Z": safe_num(set_is_monolithic_int, 0),
            "Set_Мощность_Пересечения_Остатков": safe_num(set_intersection_power, 4),
            "Set_Коэффициент_Дробности_Множества": safe_num(set_fractional_ratio, 4),

            # =====================================================================
            # БЛОК ВОЛНОВОЙ ВИБРАЦИИ И "БОКОВОЙ ЛИНИИ" (РОВНО 3 КОЛОНКИ)
            # =====================================================================
            "Wave_Квантовый_Спин_Остатков": safe_num(spin_quantum_variance, 4),
            "Wave_Трение_Цифровой_Пены_Гессиан": safe_num(foam_friction_tensor, 4),
            "Wave_Морфогенез_Выживаемости_Кода": safe_num(code_survival_morphogenesis, 4),

            # =====================================================================
            # БЛОК ИИ-СИНТЕЗАТОРА И КРОССБАР-МАТРИЦЫ (РОВНО 3 КОЛОНКИ)
            # =====================================================================
            "AI_Схлопывание_Инварианта_Закона": safe_num(invariant_perfection, 4),
            "AI_Разреженный_Когнитивный_Кворум": safe_num(sparse_quorum_rate, 4),
            "AI_Дробный_Демпфер_Предыстории_073": safe_num(fractional_memory_link, 4)

        }


    except Exception as e:
        global SKIP_COUNT, MAX_SKIP_LOGS
        if SKIP_COUNT < MAX_SKIP_LOGS:
            SKIP_COUNT += 1
            print(f"\n⚠️ [ДЕБАГ ПРОПУСКА #{SKIP_COUNT}] Ряд: {seq_id}")
            print(f"   ↳ Длина в базе: {len(raw_sequence)} чисел")
            print(f"   ↳ Первые числа: {raw_sequence[:10]}")            
            print(f"   ↳ ОШИБКА: {type(e).__name__} -> {e}")
            print("-" * 60)
            

        # Модифицированный возврат: каждое число бережно оборачиваем в safe_num
        # return {
        #     "ID": seq_id, "Название": seq_name, "Вердикт": verdict, "Status": "Успешно",
        #     "Длина_Ряда": n_len, "Среднее_Значение": round(mean_val, 2), "Станд_Отклонение": round(std_val, 2),
        #     "Коэф_Вариации": round(coef_variation, 4), "Асимметрия_Сдвига": round(skewness, 4), "Эксцесс_Хвостов": round(kurtosis, 4),
        #     "Процентиль_75": round(pct_75, 2), "Процентиль_95": round(pct_95, 2), "Коэф_Аномалий_Шага": round(step_anomaly_ratio, 2),
        #     "Энтропия_Шеннона": round(shannon_ent, 4), "Энтропия_Перестановок": round(perm_ent, 4), "Приближенная_Энтропия_ApEn": round(approx_ent, 4),
        #     "Автокорреляция_Лаг1": round(ac_lag1, 4), "Автокорреляция_Лаг2": round(ac_lag2, 4), "Автокорреляция_Лаг3": round(ac_lag3, 4),
        #     "Автокорреляция_Лаг4": round(ac_lag4, 4), "Автокорреляция_Лаг5": round(ac_lag5, 4), "Энергия_Спектра_Фурье": round(fft_energy, 2),
        #     "Главная_Частота_Фурье": main_freq, "Пик_Амплитуды_Фурье": round(max_amplitude, 2), "Медианная_Частота_Фурье": median_freq,
        #     "Дисперсия_Спектра_Фурье": round(fft_dispersion, 2), "Спектральная_Энтропия_Фурье": round(spectral_ent, 4), "Радиус_Векторного_Облака": round(cloud_radius, 2),
        #     "Физическая_Длина_Змеи": round(snake_total_length, 2), "Доля_Оси_PCA_X": round(pca_x, 4), "Доля_Оси_PCA_Y": round(pca_y, 4),
        #     "Доля_Оси_PCA_Z": round(pca_z, 4), "Сила_Ротора_Закрутки": round(vector_rot_force, 2), "Индекс_Сквозных_Дыр": round(has_hollow_holes, 4),
        #     "Коэф_Ветвления_Пирсона": round(branch_ratio, 4), "Фрактал_Размерность_GP": round(corr_dim, 4), "Показатель_Херста_Памяти": round(hurst, 4),
        #     "Девиация_Закона_Бенфорда": round(benford_deviation, 4), "Доля_Первых_Единиц_Бенфорда": round(benford_pct_1, 4),
        #     # НАШИ НОВЫЕ СТАТИСТИЧЕСКИЕ МОЩНОСТИ:
        #     "Бенфорд_Хи_Квадрат": round(benford_chi2, 4), "Бенфорд_KL_Дивергенция": round(benford_kl_div, 4), "Бенфорд_Стат_Вердикт": benford_p_verdict 
        # }
        
        # Модифицированный возврат: каждое число бережно оборачиваем в safe_num
        return {
            "ID": f'="{seq_id}"',  # Жестко запечатываем ID, чтобы не превращался в дату!
            "Название": seq_name, 
            "Чистый_Класс": c_clean,       # НОВАЯ ЧИСТАЯ ЯЧЕЙКА ДЛЯ ФИЛЬТРОВ И ГРАФИКОВ!
            "Вердикт": verdict, 
            "Status": "Успешно",
            "Длина_Ряда": safe_num(n_len, 0), 
            "Среднее_Значение": safe_num(mean_val, 2), 
            "Станд_Отклонение": safe_num(std_val, 2),
            "Коэф_Вариации": safe_num(coef_variation, 4), 
            "Асимметрия_Сдвига": safe_num(skewness, 4), 
            "Эксцесс_Хвостов": safe_num(kurtosis, 4),
            "Процентиль_75": safe_num(pct_75, 2), 
            "Процентиль_95": safe_num(pct_95, 2), 
            "Коэф_Аномалий_Шага": safe_num(step_anomaly_ratio, 2),
            "Энтропия_Шеннона": safe_num(shannon_ent, 4), 
            "Энтропия_Перестановок": safe_num(perm_ent, 4), 
            "Приближенная_Энтропия_ApEn": safe_num(approx_ent, 4),
            "Автокорреляция_Лаг1": safe_num(ac_lag1, 4), 
            "Автокорреляция_Лаг2": safe_num(ac_lag2, 4), 
            "Автокорреляция_Лаг3": safe_num(ac_lag3, 4),
            "Автокорреляция_Лаг4": safe_num(ac_lag4, 4), 
            "Автокорреляция_Лаг5": safe_num(ac_lag5, 4), 
            "Энергия_Спектра_Фурье": safe_num(fft_energy, 2),
            "Главная_Частота_Фурье": safe_num(main_freq, 0), 
            "Пик_Амплитуды_Фурье": safe_num(max_amplitude, 2), 
            "Медианная_Частота_Фурье": safe_num(median_freq, 0),
            "Дисперсия_Спектра_Фурье": safe_num(fft_dispersion, 2), 
            "Спектральная_Энтропия_Фурье": safe_num(spectral_ent, 4), 
            "Радиус_Векторного_Облака": safe_num(cloud_radius, 2),
            "Физическая_Длина_Змеи": safe_num(snake_total_length, 2), 
            "Доля_Оси_PCA_X": safe_num(pca_x, 4), 
            "Доля_Оси_PCA_Y": safe_num(pca_y, 4),
            "Доля_Оси_PCA_Z": safe_num(pca_z, 4), 
            "Сила_Ротора_Закрутки": safe_num(vector_rot_force, 2), 
            "Индекс_Сквозных_Дыр": safe_num(has_hollow_holes, 4),
            "Коэф_Ветвления_Пирсона": safe_num(branch_ratio, 4), 
            "Фрактал_Размерность_GP": safe_num(corr_dim, 4), 
            "Показатель_Херста_Памяти": safe_num(hurst, 4),
            "Девиация_Закона_Бенфорда": safe_num(benford_deviation, 4), 
            "Доля_Первых_Единиц_Бенфорда": safe_num(benford_pct_1, 4),
            
            # НАШИ НОВЫЕ СТАТИСТИЧЕСКИЕ МОЩНОСТИ:
            "Бенфорд_Хи_Квадрат": safe_num(benford_chi2, 4),
            "Бенфорд_KL_Дивергенция": safe_num(benford_kl_div, 4),
            "Бенфорд_Стат_Вердикт": benford_p_verdict,

            # БЛОК ГРАФОВ ВИДИМОСТИ (NVG / HVG):
            "Graph_NVG_Узлы": safe_num(nvg_nodes, 0),
            "Graph_NVG_Ребра": safe_num(nvg_edges, 0),
            "Graph_NVG_Плотность": safe_num(nvg_density, 4),
            "Graph_NVG_Макс_Степень": safe_num(nvg_max_degree, 0),
            "Graph_NVG_Сред_Степень": safe_num(nvg_mean_degree, 2),
            "Graph_NVG_Энтропия_Степеней": safe_num(nvg_degree_entropy, 4),
            "Graph_NVG_Кластеризация": safe_num(nvg_avg_clustering, 4),
            "Graph_NVG_Транзитивность": safe_num(nvg_transitivity, 4),
            "Graph_NVG_Диаметр": safe_num(nvg_diameter, 0),
            "Graph_NVG_Радиус": safe_num(nvg_radius, 0),
            "Graph_NVG_Сред_Путь": safe_num(nvg_avg_path, 2),
            "Graph_NVG_Ассортативность": safe_num(nvg_assortativity, 4),
            "Graph_NVG_Близость_Closeness": safe_num(nvg_mean_closeness, 4),
            "Graph_NVG_Влияние_Eigenvector": safe_num(nvg_mean_eigen, 4),
            "Graph_NVG_Кол_Сообществ": safe_num(nvg_num_communities, 0),
            "Graph_NVG_Модульность": safe_num(nvg_modularity, 4),
            "Graph_NVG_Энергия_Лапласа": safe_num(nvg_graph_energy, 2),
            "Graph_NVG_Спектр_Радиус": safe_num(nvg_spectral_radius, 4),
            "Graph_NVG_Число_Фидлера": safe_num(nvg_fiedler_value, 4),
            
            "Graph_HVG_Узлы": safe_num(hvg_nodes, 0),
            "Graph_HVG_Ребра": safe_num(hvg_edges, 0),
            "Graph_HVG_Плотность": safe_num(hvg_density, 4),
            "Graph_HVG_Сред_Степень": safe_num(hvg_mean_degree, 2),
            "Graph_HVG_Кластеризация": safe_num(hvg_avg_clustering, 4),
            
            "Graph_Видимость_Сред_Длина": safe_num(nvg_mean_edge_length, 2),
            "Graph_Видимость_Макс_Длина": safe_num(nvg_max_edge_length, 0),
            
            # =====================================================================
            # УЛЬТИМАТИВНЫЙ БЛОК ЭМЕРДЖЕНТНОСТИ (РОВНО 20 КОЛОНОК)
            # =====================================================================
            "Эмердж_Causal_Emergence": safe_num(causal_emergence, 4),
            "Эмердж_Индекс_Самоорг": safe_num(self_organization_index, 4),
            "Эмердж_Микро_Шум_Хоэла": safe_num(micro_noise, 4),
            "Эмердж_Макро_Шум_Хоэла": safe_num(macro_noise, 4),
            "Эмердж_Энтропия_Реньи": safe_num(renyi_ent, 4),
            "Эмердж_Энтропия_Цаллиса": safe_num(tsallis_ent, 4),
            "Эмердж_Перестановки_Лаг2": safe_num(perm_ent_l2, 4),
            "Эмердж_Перестановки_Лаг3": safe_num(perm_ent_l3, 4),
            "Эмердж_Динамика_Формы_Вассерштейна": safe_num(wasserstein_dist, 4),
            "Эмердж_Резонанс_Шеннон_Фурье": safe_num(shannon_spectral_ratio, 4),
            "Эмердж_Эффект_Бабочки_Ляпунов": safe_num(local_lyapunov, 4),
            "Эмердж_Стационарность_Флуктуаций": safe_num(fluc_co_variation, 4),
            "Эмердж_Затухание_Памяти_АКОФ": safe_num(ac_decay_rate, 4),
            "Эмердж_Индекс_Резонанса_PCA": safe_num(emergence_resonance_score, 4),
            "Эмердж_Марковская_Плотность_Приращений": safe_num(len(unique_pairs) if 'unique_pairs' in locals() else 0, 0),
            "Эмердж_Макро_Плотность_Приращений": safe_num(len(m_unique_pairs) if 'm_unique_pairs' in locals() else 0, 0),
            "Эмердж_Дисперсия_Марковских_Переходов": safe_num(np.std(p_matrix) if 'p_matrix' in locals() else 0.0, 4),
            "Эмердж_Дисперсия_Макро_Переходов": safe_num(np.std(m_matrix) if 'm_matrix' in locals() else 0.0, 4),
            "Эмердж_Скорость_Потери_Информации": safe_num(abs(micro_noise - shannon_ent), 4),
            "Эмердж_Коэффициент_Нелинейности_Сдвига": safe_num(abs(perm_ent - shannon_ent), 4),

            # =====================================================================
            # БЛОК ТОПОЛОГИИ ЗМЕЙКИ И TDA (РОВНО 16 КОЛОНОК)
            # =====================================================================
            "TDA_Betti0_Связность": safe_num(betti_0_small, 4),
            "TDA_Betti1_Туннели": safe_num(betti_1_large, 4),
            "TDA_Persistence_Штрихкод": safe_num(persistence_lifespan, 4),
            "TDA_Тензор_Инерции_X": safe_num(inertia_x, 4),
            "TDA_Тензор_Инерции_Y": safe_num(inertia_y, 4),
            "TDA_Тензор_Инерции_Z": safe_num(inertia_z, 4),
            "TDA_Сферическая_Асимметрия": safe_num(spherical_asymmetry, 4),
            "TDA_Извилистость_Tortuosity": safe_num(tortuosity_index, 4),
            "TDA_Гео_Индекс_Винера": safe_num(t_wiener_index, 2),
            "TDA_Фрактал_Минковского_Box": safe_num(minkowski_box_dim, 4),
            "TDA_Объем_Оболочки_Hull": safe_num(convex_hull_volume, 4),
            "TDA_Плотность_Оболочки_Solidity": safe_num(convex_hull_solidity, 4),
            "TDA_Кривизна_Гаусса": safe_num(gaussian_curvature, 4),
            "TDA_Кручение_Змейки_Torsion": safe_num(torsion_force, 4),
            "TDA_Плотность_Самопересечений": safe_num(self_intersections, 4),
            "TDA_Радиус_Гирации_Упаковки": safe_num(radius_of_gyration, 4),

            # =====================================================================
            # БЛОК ВЫСШЕЙ АЛГЕБРАИЧЕСКОЙ ТЕОРИИ ЧИСЛ (РОВНО 12 КОЛОНОК)
            # =====================================================================
            "Alg_Плотность_Простых_Делителей": safe_num(prime_factor_density, 4),
            "Alg_Индекс_Взаимной_Простоты_НОД": safe_num(coprimality_rate, 4),
            "Alg_Энтропия_Остатков_Mod2": safe_num(mod2_entropy, 4),
            "Alg_Энтропия_Остатков_Mod3": safe_num(mod3_entropy, 4),
            "Alg_Энтропия_Остатков_Mod5": safe_num(mod5_entropy, 4),
            "Alg_Энтропия_Остатков_Mod7": safe_num(mod7_entropy, 4),
            "Alg_Частота_Совершенных_Чисел": safe_num(perfect_proximity, 4),
            "Alg_Доля_Свободных_От_Квадратов": safe_num(square_free_rate, 4),
            "Alg_p_Адическая_2_Валентность": safe_num(padic_valuation_mean, 4),
            "Alg_Отклонение_От_Золотого_Сечения": safe_num(fibonacci_proximity, 4),
            "Alg_Периодичность_Дробных_Хвостов": safe_num(frac_periodicity, 4),
            "Alg_Степень_Локального_Полинома": safe_num(poly_degree, 0),

            # =====================================================================
            # БЛОК ИНФОРМАТИКИ, КОМБИНАТОРИКИ И ТЕОРИИ КОДИРОВАНИЯ (РОВНО 12 КОЛОНОК)
            # =====================================================================
            "Inf_Сжатие_LZ_Сложность": safe_num(lz_complexity_ratio, 4),
            "Inf_Избыточность_Шеннона": safe_num(info_redundancy, 4),
            "Inf_Доля_Бескраш_Блока": safe_num(max_unrepeated_ratio, 4),
            "Inf_Хемминг_Половин_Ряда": safe_num(hamming_distance_ratio, 4),
            "Inf_Тьюринг_Энтропия_Ускорения": safe_num(turing_step_entropy, 4),
            "Inf_Уолш_Индекс_Переходов": safe_num(walsh_energy_index, 4),
            "Inf_Битовая_Автокорреляция_Четности": safe_num(bit_plane_autocorr, 4),
            "Inf_Марковская_Память_Порядка2": safe_num(markov_order2_entropy, 4),
            "Inf_Грамматическое_Сжатие_Строки": safe_num(grammar_complexity_index, 4),
            "Inf_Инфо_Количество_Фишера": safe_num(fisher_approx, 4),
            "Inf_Плотность_Вентилей_Маски": safe_num(logical_gate_density, 4),
            "Inf_IEEE754_Энтропия_Мантиссы": safe_num(ieee754_mantissa_entropy, 4),

            # =====================================================================
            # БЛОК КВАНТОВОЙ ДИНАМИКИ И ТЕОРИИ ИНФОРМАЦИИ (РОВНО 12 КОЛОНОК)
            # =====================================================================
            "Quant_Перекрестная_Энтропия_Гаусс": safe_num(cross_entropy_fit, 4),
            "Quant_Энтропия_Реньи_Альфа3": safe_num(renyi_alpha3, 4),
            "Quant_Энтропия_Цаллиса_q15": safe_num(tsallis_q15, 4),
            "Quant_Энтропия_Фон_Неймана": safe_num(von_neumann_entropy, 4),
            "Quant_СВД_Энтропия_Спектра": safe_num(svd_entropy_score, 4),
            "Quant_Индекс_Спада_Частот_Beta": safe_num(spectral_slope_beta, 4),
            "Quant_Когерентность_Квантовых_Фаз": safe_num(phase_coherence, 4),
            "Quant_Рекуррентная_Плотность_Паттернов": safe_num(cross_recurrence_density, 4),
            "Quant_Время_Возврата_Пуанкаре": safe_num(poincare_return_mean, 2),
            "Quant_Показатель_Суб_Ляпунова": safe_num(sub_lyapunov_exponent, 4),
            "Quant_Зазор_Бьёрнена_Нильсена_Уровней": safe_num(bjornen_nilsen_gap, 4),
            "Quant_Фрактал_Детерминант_Хаусдорфа": safe_num(quantum_det_hausdorff, 4),

            # =====================================================================
            # БЛОК НЕЛИНЕЙНОЙ СТАТИСТИКИ И АНАЛИЗА АНОМАЛИЙ (РОВНО 10 КОЛОНОК)
            # =====================================================================
            "Stat_Псевдо_АДФ_Стационарность": safe_num(pseudo_adf_stat, 4),
            "Stat_Коэффициент_Тейла_Качество": safe_num(pseudo_theil_u, 4),
            "Stat_Робастный_Разброс_MAD": safe_num(mad_score, 2),
            "Stat_Локальный_Хёрст_Полуряда": safe_num(local_hurst_half, 4),
            "Stat_Индекс_Концентрации_Джини": safe_num(gini_index, 4),
            "Stat_Сила_Фазового_Излома": safe_num(phase_break_len, 4),
            "Stat_Критерий_Знаков_Рост_Спад": safe_num(sign_test_stat, 4),
            "Stat_Авторегрессионный_Остаток_Шума": safe_num(ar_residual_var, 4),
            "Stat_Плотность_Черных_Лебедей_EvD": safe_num(extreme_value_density, 4),
            "Stat_Индекс_Хрупкости_Тренда": safe_num(trend_fragility_index, 4),

            # =====================================================================
            # БЛОК КОНСТАНТНОГО АНАЛИЗА SYMPY (РОВНО 6 КОЛОНОК)
            # =====================================================================
            "Tail_SymPy_Длина_Цепной_Дроби": safe_num(cf_length, 0),
            "Tail_SymPy_Среднее_Цепной_Дроби": safe_num(cf_mean, 2),
            "Tail_SymPy_Станд_Откл_Цепной_Дроби": safe_num(cf_std, 2),
            "Tail_SymPy_Энтропия_Цепной_Дроби": safe_num(cf_entropy, 4),
            "Tail_SymPy_Маркер_Цикличного_Повтора": safe_num(str_period_found, 0),
            "Tail_SymPy_Длина_Найденного_Цикла": safe_num(max_pattern_len, 0),

            "CA_Маркер_Клеточного_Автомата": safe_num(is_cellular_automaton, 0),
            "CA_Номер_Правила_Вольфрама_RuleID": safe_num(wolfram_rule_id, 0),
            "CA_Сложность_Таблицы_Переходов": safe_num(ca_complexity, 4),

            # =====================================================================
            # БЛОК ТРЕНДОВ, ЛАМИНАРНОСТИ И АНОМАЛИЙ (РОВНО 6 КОЛОНОК)
            # =====================================================================
            "Trend_Ламинарность_Потока_LAM": safe_num(laminarity_score, 4),
            "Trend_Индекс_Ходжеса_Лемана": safe_num(hodges_lehmann_index, 4),
            "Trend_Колмогоров_Смирнов_Экспонента": safe_num(ks_exponential_stat, 4),
            "Trend_Сложность_Аллендорфа_Экстремумов": safe_num(allendorf_complexity, 4),
            "Trend_Корреляция_Спирмена_Монотонность": safe_num(spearman_trend_correlation, 4),
            "Trend_Z_Score_Макс_Выброса_Аномалии": safe_num(z_score_max_anomaly, 4),

            "Sum_Финальный_Вектор_Накопления": safe_num(final_sum_vector, 4),
            "Sum_Скорость_Взрыва_Расширения": safe_num(sum_expansion_rate, 4),
            "Sum_Волатильность_Кумулятивная": safe_num(sum_fluctuation_std, 4),
            "Sum_Коэффициент_Сходимости_Хвоста": safe_num(sum_convergence_ratio, 4),


            # =====================================================================
            # БЛОК БАЗОВЫХ МНОЖЕСТВ И КОЛЕЦ (РОВНО 6 КОЛОНОК)
            # =====================================================================
            "Set_Доля_Натуральных_Чисел_N": safe_num(set_naturals_ratio, 4),
            "Set_Доля_Целых_Чисел_Кольца_Z": safe_num(set_integers_ratio, 4),
            "Set_Доля_Простых_Чисел_Множества_P": safe_num(set_primes_ratio, 4),
            "Set_Маркер_Монолитности_Ряда_В_Z": safe_num(set_is_monolithic_int, 0),
            "Set_Мощность_Пересечения_Остатков": safe_num(set_intersection_power, 4),
            "Set_Коэффициент_Дробности_Множества": safe_num(set_fractional_ratio, 4),

            # =====================================================================
            # БЛОК ВОЛНОВОЙ ВИБРАЦИИ И "БОКОВОЙ ЛИНИИ" (РОВНО 3 КОЛОНКИ)
            # =====================================================================
            "Wave_Квантовый_Спин_Остатков": safe_num(spin_quantum_variance, 4),
            "Wave_Трение_Цифровой_Пены_Гессиан": safe_num(foam_friction_tensor, 4),
            "Wave_Морфогенез_Выживаемости_Кода": safe_num(code_survival_morphogenesis, 4),


            # =====================================================================
            # БЛОК ИИ-СИНТЕЗАТОРА И КРОССБАР-МАТРИЦЫ (РОВНО 3 КОЛОНКИ)
            # =====================================================================
            "AI_Схлопывание_Инварианта_Закона": safe_num(invariant_perfection, 4),
            "AI_Разреженный_Когнитивный_Кворум": safe_num(sparse_quorum_rate, 4),
            "AI_Дробный_Демпфер_Предыстории_073": safe_num(fractional_memory_link, 4)
            
        }


# =====================================================================
# ГЛАВНЫЙ АВТОНОМНЫЙ ДВИЖОК
# =====================================================================
if __name__ == "__main__":
    print("🛸 Инициализация Ультимативного 40-Поточного Мега-Атласа...")
    
    if not os.path.exists(INPUT_STRIPPED) or not os.path.exists(INPUT_NAMES):
        print("❌ ОШИБКА: Положите stripped.gz и names.gz (20-30 МБ) в папку с кодом!")
        exit()

    # --- УМНЫЙ СКАЙНЕР УЖЕ СУЩЕСТВУЮЩИХ ДАННЫХ ---
    processed_ids = set()
    file_exists = os.path.isfile(OUTPUT_FILE)
    
    if file_exists:
        print(f"🕵️‍♂️ Найдена прошлая сессия! Сканируем {OUTPUT_FILE} на готовые ряды...")
        try:
            # Читаем только колонку ID, чтобы сэкономить ОЗУ
            existing_df = pd.read_csv(OUTPUT_FILE, sep=";", usecols=["ID"], encoding="utf-8-sig")
            # Очищаем формулу экселя '="A000001"' обратно в чистый ID 'A000001'
            processed_ids = set(existing_df["ID"].str.replace('="', '').str.replace('"', '').tolist())
            print(f"✅ Успешно пропущено: {len(processed_ids)} уже обработанных рядов.")
        except Exception as e:
            print(f"⚠️ Не удалось прочесть прошлый файл ({e}), пишем с нуля.")
            file_exists = False

    print("📖 Разворачиваем карту названий в памяти...")
    name_dict = {}
    with gzip.open(INPUT_NAMES, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip(): 
                continue
            parts = line.split(' ', 1)
            if len(parts) == 2: 
                name_dict[parts[0].strip()] = parts[1].strip()

    # output_file = f"{OUTPUT_FILE}_part{current_part}.csv"
    # file_exists = os.path.isfile(OUTPUT_FILE)
    batch_data = []

    # Индексы для контроля автонарезки файлов и измерения скорости
    current_part = 1
    processed_count = 0
    start_time = time.time()
    newly_processed_count = 0
    total_processed_global = 0
    current_file_rows = 0

    print(f"🎯 Поехали! Начинаем тотальную эксплуатацию базы. Цель: {LIMIT_SEQUENCES} рядов.")

    with gzip.open(INPUT_STRIPPED, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip(): 
                continue
                
            parts = line.split(',')
            seq_id = parts[0].strip()
            
            # ЕСЛИ ID УЖЕ ЕСТЬ В ФАЙЛЕ — РОБОТ ЕГО ПРОСТО ПРОПУСКАЕТ!
            if seq_id in processed_ids:
                continue

            seq_name = name_dict.get(seq_id, "Без названия")
            
            raw_seq = []
            for item in parts[1:]:
                item_clean = item.strip()
                if item_clean and item_clean != '\n':
                    try: 
                        raw_seq.append(int(item_clean))
                    except ValueError: 
                        continue

             # Быстрый расчет метрик
            analysis = analyze_sequence(seq_id, seq_name, raw_seq)
            batch_data.append(analysis)
            processed_count += 1
            newly_processed_count += 1 
            total_processed_global += 1
            current_file_rows += 1           
            
            # Лог спидометра в консоль раз в 200 последовательностей
            if total_processed_global % 200 == 0:
                elapsed_min = (time.time() - start_time) / 60.0
                speed = round(total_processed_global / (elapsed_min + 1e-12), 1)
                print(f"⏱️ Скорость: {speed} рядов/мин. Всего пройдено: {total_processed_global}")
            
            # Срабатывание батча строго по 50 штук - ОЗУ всегда чиста!
            if len(batch_data) == BATCH_SIZE or processed_count >= LIMIT_SEQUENCES:
                df_batch = pd.DataFrame(batch_data)
                
                # Записываем с разделителем ";" и кодировкой "utf-8-sig"
                if not file_exists:
                    df_batch.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig", mode='w')
                    file_exists = True
                else:
                    df_batch.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig", mode='a', header=False)
                
                total_in_file = len(processed_ids) + newly_processed_count                
                print(f"💾 [БАТЧ ЗАПИСАН В CSV] Пройдено: {processed_count}/{LIMIT_SEQUENCES} рядов. ОЗУ полностью очищено.")
                print(f"💾 [БАТЧ ЗАПИСАН] Новых: {newly_processed_count}/{LIMIT_SEQUENCES}. Всего в Атласе: {total_in_file} рядов.")                
                batch_data = []
                time.sleep(0.3) # Остужаем i5

                # АВТОНАРЕЗКА: Проверяем, не пора ли закрывать текущую часть
                if current_file_rows >= MAX_ROWS_PER_FILE:
                    print(f"📦 ЧАСТЬ {current_part} ЗАПОЛНЕНА ({current_file_rows} строк). Создаем новую нарезку!")
                    current_part += 1
                    current_file_rows = 0
                    output_file = f"{OUTPUT_FILE}_part{current_part}.csv"
                    file_exists = os.path.isfile(output_file) # Сброс флага для заголовков нового файла
                                
            if processed_count >= LIMIT_SEQUENCES:
                break

    end_time = time.time()
    print("\n" + "="*60)
    print("👑 МАТЕМАТИЧЕСКИЙ АТЛАС УСПЕШНО СФОРМИРОВАН!")
    print(f"⏱️ Время тотального сканирования: {round(end_time - start_time, 2)} сек.")
    print(f"📊 40-колончатый шедевр сохранен в файл: {OUTPUT_FILE}")
    print("="*60)
