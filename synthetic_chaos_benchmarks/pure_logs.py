import numpy as np
import pandas as pd

def safe_log(x, base=np.e):
    """
    Универсальная защита логарифма от нулей, отрицательных чисел 
    и ухода в минус бесконечность.
    """
    val = np.abs(x) + 1e-9
    if base == 10:
        return np.log10(val)
    elif base == 2:
        return np.log2(val)
    return np.log(val)

def generate_pure_log_ring(variant_idx):
    """
    Создает базовый ряд из 100 чисел, прогоняя его через 5 каскадов
    исключительно логарифмических трансформаций.
    """
    # Стартовый вектор: от 1 до 100
    x = np.arange(1, 101, dtype=float)
    
    # 7 уникальных логарифмических колец (мутаторов)
    for step in range(5):
        op_selector = (variant_idx + step) % 7
        
        if op_selector == 0:
            x = safe_log(x, base=np.e) * 15.0            # Натуральный логарифм с масштабом
        elif op_selector == 1:
            x = safe_log(x, base=10) * 50.0             # Десятичный логарифм
        elif op_selector == 2:
            x = safe_log(x, base=2) * 8.0               # Двоичный логарифм
        elif op_selector == 3:
            x = x * safe_log(np.sin(x) * 10)            # Логарифмическая волна (синус-маска)
        elif op_selector == 4:
            x = safe_log(x ** 2) / 2.0                  # Логарифм степенного аргумента
        elif op_selector == 5:
            x = safe_log(x + 25.0) * 1.618              # Логарифм со сдвигом через Золотое Сечение
        elif op_selector == 6:
            x = x - safe_log(x) * 12.0                  # Возвратная логарифмическая петля
            
    return x

# Инициализация сборки датасета (28 вариантов * 35 мутаций = 980 рядов)
all_log_rows = []
total_variants = 28
mutations_per_variant = 35

for v in range(total_variants):
    # Генерируем чистое логарифмическое ядро для этого класса
    base_log_seq = generate_pure_log_ring(v)
    
    # Записываем точную формулу каскада в Паспорт
    ops_used = [(v + s) % 7 for s in range(5)]
    passport = f"Log_Core_Class_{v+1}__Cascade_{ops_used}"
    
    for m in range(mutations_per_variant):
        # 1% чистый белый шум индивидуально на каждую точку (мутация)
        pure_random_noise = np.random.uniform(0.99, 1.01, size=100)
        mutated_log_seq = base_log_seq * pure_random_noise
        
        # Собираем строку данных для экспорта
        row_data = {
            "Global_Row_ID": (v * mutations_per_variant) + m + 1,
            "Log_Class_ID": v + 1,                       # ID логарифмического семейства
            "Mutation_ID": m + 1,                        # ID мутации внутри семейства
            "Passport_Formula": passport                 # Генетический паспорт ряда
        }
        
        # Разворачиваем 100 чисел в колонки таблицы
        for num_idx, val in enumerate(mutated_log_seq):
            # Защита от NaN/Inf в финальной таблице на всякий случай
            if np.isnan(val) or np.isinf(val):
                val = 0.0
            row_data[f"Num_{num_idx+1}"] = val
            
        all_log_rows.append(row_data)

# Упаковываем в DataFrame и сохраняем
df_log = pd.DataFrame(all_log_rows)
df_log.to_csv("synthetic_pure_logs_980.csv", index=False)

print(f" Фабрика логарифмов отработала! Создано рядов: {df_log.shape[0]}")
print(f" Таблица 'synthetic_pure_logs_980.csv' успешно собрана и снабжена Паспортами.")
