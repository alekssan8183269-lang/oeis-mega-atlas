import numpy as np
import pandas as pd
import os

# ==========================================
# ЯЩИК С ДЕТАЛЯМИ LEGO: БАЗОВЫЕ ПОД-ПРОГРАММЫ
# ==========================================

def safe_log(x, base=np.e):
    val = np.abs(x) + 1e-9
    if base == 10: return np.log10(val)
    if base == 2: return np.log2(val)
    return np.log(val)

def generate_colored_noise(length, noise_type):
    """ Генератор спектральных физических шумов """
    if noise_type == "white": return np.random.normal(0, 1, length)
    elif noise_type == "pink":
        X_white = np.random.normal(0, 1, length)
        X_fourier = np.fft.rfft(X_white)
        frequencies = np.fft.rfftfreq(length) + 1e-9
        X_fourier = X_fourier / np.sqrt(frequencies)
        result = np.fft.irfft(X_fourier, length)
        return result / (np.std(result) + 1e-9)
    elif noise_type == "red":
        return np.cumsum(np.random.normal(0, 1, length))
    elif noise_type == "blue":
        white = np.random.normal(0, 1, length + 1)
        result = np.diff(white)
        return result / (np.std(result) + 1e-9)
    elif noise_type == "black":
        base = np.random.normal(0, 0.1, length)
        spike_indices = np.random.choice(length, size=np.random.randint(1, 3), replace=False)
        for idx in spike_indices:
            base[idx] += np.random.choice([-1, 1]) * np.random.uniform(15.0, 30.0)
        return base
    return np.zeros(length)

def get_quad_area(quad_type, idx):
    """ Генератор честных площадей геометрических фигур """
    scale = (idx + 1) * 1.5
    if quad_type == "parallelogram":
        return np.random.uniform(5.0, 15.0) * np.random.uniform(4.0, 12.0) * scale
    elif quad_type == "trapezoid":
        return ((np.random.uniform(6.0, 18.0) + np.random.uniform(4.0, 14.0)) / 2.0) * np.random.uniform(5.0, 10.0) * scale
    elif quad_type == "rhombus":
        return (np.random.uniform(8.0, 20.0) * np.random.uniform(6.0, 16.0) / 2.0) * scale
    elif quad_type == "rectangle":
        return np.random.uniform(5.0, 25.0) * np.random.uniform(3.0, 15.0) * scale
    return 1.0

# ==========================================
# ДВИЖОК СБОРКИ КАСКАДНЫХ КОЛЕЦ
# ==========================================

def execute_lego_brick(x, brick_id, seq_length):
    """
    Применяет выбранную LEGO-деталь к числовому ряду.
    Доступно 16 уникальных блоков (0-15).
    """
    # --- КАТЕГОРИЯ А: ЧИСТАЯ МАТЕМАТИКА ---
    if brick_id == 0:   return x / 20.0                                          # Деление на 20
    elif brick_id == 1: return x * safe_log(x, np.e)                             # Умножение на натуральный лог
    elif brick_id == 2: return x + np.sin(x) * 15.0                              # Синусоидальное кручение
    elif brick_id == 3: return x * 1.618                                         # Пропорция Золотого Сечения
    elif brick_id == 4: return np.sign(x) * (np.abs(x) ** 1.05)                  # Степенная деформация
    elif brick_id == 5: return x + (x % 7) * 3.0                                 # Модульный решетчатый сдвиг
    elif brick_id == 6: return x - np.cos(x) * 8.0                               # Косинусоидальное трение
    
    # --- КАТЕГОРИЯ Б: ЛОГАРИФМИЧЕСКИЕ СТРЕСС-БЛОКИ ---
    elif brick_id == 7: return safe_log(x, base=10) * 50.0                        # Десятичный лог
    elif brick_id == 8: return safe_log(x, base=2) * 8.0                          # Двоичный лог
    elif brick_id == 9: return x * safe_log(np.sin(x) * 10.0)                    # Логарифмическая волна
    
    # --- КАТЕГОРИЯ В: ХРОМАТИЧЕСКИЕ ШУМЫ ---
    elif brick_id == 10: return x + generate_colored_noise(seq_length, "red") * 5.0    # Красный шум (Браун)
    elif brick_id == 11: return x + generate_colored_noise(seq_length, "blue") * 4.0   # Синий шум (Пила)
    elif brick_id == 12: return x * (1.0 + generate_colored_noise(seq_length, "pink") * 0.2) # Розовый фрактал
    elif brick_id == 13: return x + generate_colored_noise(seq_length, "black")        # Черный шум (Катастрофа)
    
    # --- КАТЕГОРИЯ Г: ГЕОМЕТРИЧЕСКИЕ ПЛОЩАДИ ---
    elif brick_id == 14: # Каскад площадей параллелограмм/трапеция
        geo_array = np.array([get_quad_area("parallelogram" if i%2==0 else "trapezoid", i) for i in range(seq_length)])
        return x + geo_array * 0.5
    elif brick_id == 15: # Каскад площадей ромб/прямоугольник
        geo_array = np.array([get_quad_area("rhombus" if i%2==0 else "rectangle", i) for i in range(seq_length)])
        return x + geo_array * 0.5

    return x

# ==========================================
# ИНТЕРФЕЙС УПРАВЛЕНИЯ ЭКСПЕРИМЕНТОМ (КОНФИГ)
# ==========================================

def run_lego_experiment(lego_slots, sequence_length=100, mutation_percent=1.0, filename="lego_chaos_output.csv"):
    """
    Генерирует 28 классов по 35 мутаций (980 рядов).
    Каждый класс получает циклическое смещение выбранных пользователем LEGO-блоков.
    """
    assert len(lego_slots) == 5, "Бро, в конструкторе должно быть ровно 5 слотов для колец!"
    
    # Имена деталей для записи в генетический паспорт
    brick_names = {
        0: "Div20", 1: "NatLog", 2: "SinWave", 3: "GoldenRatio", 4: "PowerWarp", 5: "ModShift", 6: "CosWave",
        7: "Log10", 8: "Log2", 9: "LogSin", 10: "RedNoise", 11: "BlueNoise", 12: "PinkNoise", 13: "BlackNoise",
        14: "Geo_ParaTrap", 15: "Geo_RhomRect"
    }

    all_generated_rows = []
    total_variants = 28
    mutations_per_variant = 35

    print(f"🧱 Конструктор LEGO активирован. Сборка каскада: {[brick_names[b] for b in lego_slots]}")
    print(f"⚙️ Параметры: Длина ряда = {sequence_length} точек, Мутация = {mutation_percent}%")

    for v in range(total_variants):
        # Формируем динамический каскад для текущего класса (циклический сдвиг пользовательского LEGO-набора)
        current_cascade = [lego_slots[(v + step) % 5] for step in range(5)]
        
        # Строим базовый вектор
        x_base = np.arange(1, sequence_length + 1, dtype=float)
        
        # Прогоняем вектор сквозь собранные LEGO-кольца
        for brick in current_cascade:
            x_base = execute_lego_brick(x_base, brick, sequence_length)
            
        # Формируем текстовый паспорт ДНК ряда
        cascade_formula = " -> ".join([brick_names[b] for b in current_cascade])
        passport = f"Lego_Class_{v+1}__[ {cascade_formula} ]"
        
        for m in range(mutations_per_variant):
            # Накладываем пользовательский уровень мутации (белый шум)
            noise_bound = mutation_percent / 100.0
            mutation_noise = np.random.uniform(1.0 - noise_bound, 1.0 + noise_bound, size=sequence_length)
            mutated_sequence = x_base * mutation_noise
            
            row_data = {
                "Global_Row_ID": (v * mutations_per_variant) + m + 1,
                "Lego_Class_ID": v + 1,
                "Mutation_ID": m + 1,
                "Passport_Formula": passport
            }
            
            for num_idx, val in enumerate(mutated_sequence):
                if np.isnan(val) or np.isinf(val): val = 0.0
                row_data[f"Num_{num_idx+1}"] = val
                
            all_generated_rows.append(row_data)

    df = pd.DataFrame(all_generated_rows)
    df.to_csv(filename, index=False)
    print(f"🎉 Эксперимент успешно завершен! Файл '{filename}' готов. Создано рядов: {df.shape}\n")

# ==========================================
# ЗАПУСК ТВОИХ СУПЕР-ЭКСПЕРИМЕНТОВ
# ==========================================
if __name__ == "__main__":
    
    # ЭКСПЕРИМЕНТ №1: "Кибер-Геометрия" (Смешиваем Золотое сечение, площади ромбов, красный и синий шумы)
    # Используем блоки: 3 (GoldenRatio), 15 (Geo_RhomRect), 10 (RedNoise), 11 (BlueNoise), 4 (PowerWarp)
    run_lego_experiment(
        lego_slots = [3, 15, 10, 11, 4],
        sequence_length = 100,
        mutation_percent = 1.0,
        filename = "lego_cyber_geometry_980.csv"
    )
    
    # ЭКСПЕРИМЕНТ №2: "Чистый Логарифмический Шум катастроф" (Логарифмы, синусы и черный шум)
    # Используем блоки: 7 (Log10), 9 (LogSin), 13 (BlackNoise), 2 (SinWave), 1 (NatLog)
    run_lego_experiment(
        lego_slots = [7, 9, 13, 2, 1],
        sequence_length = 100,
        mutation_percent = 1.5, # Чуть больше шума
        filename = "lego_log_catastrophe_980.csv"
    )
