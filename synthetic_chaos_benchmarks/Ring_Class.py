import numpy as np
import pandas as pd

def safe_log(x):
    """Защита от нулей и отрицательных чисел для логарифма"""
    return np.log(np.abs(x) + 1e-9)

def generate_ring_sequence(variant_idx):
    """
    Создает базовый ряд из 100 чисел.
    Прогоняет через 5 последовательных математических колец-трансформаций.
    """
    # Стартовый ряд: от 1 до 100
    x = np.arange(1, 101, dtype=float)
    
    # Пул из 7 различных математических операций
    # Комбинация шагов уникальна для каждого из 28 вариантов
    for step in range(5):
        op_selector = (variant_idx + step) % 7
        
        if op_selector == 0:
            x = x / 20.0                                 # Деление на 20
        elif op_selector == 1:
            x = x * safe_log(x)                          # Умножение на логарифм
        elif op_selector == 2:
            x = x + np.sin(x) * 15                       # Синусоидальное смещение
        elif op_selector == 3:
            x = x * 1.618                                # Золотое сечение (масштаб)
        elif op_selector == 4:
            x = np.sign(x) * (np.abs(x) ** 1.05)         # Нелинейное степенное сжатие
        elif op_selector == 5:
            x = x + (x % 7) * 3                          # Модульный дискретный сдвиг
        elif op_selector == 6:
            x = x - np.cos(x) * 8                        # Косинусоидальный хаос
            
    return x

# Собираем датасет: 28 вариантов по 35 мутаций каждого = 980 рядов
all_rows = []
total_variants = 28
mutations_per_variant = 35

for v in range(total_variants):
    # Генерируем "чистый" родительский ряд для данного кольца
    base_seq = generate_ring_sequence(v)
    
    # Формируем текстовый паспорт формулы (какие кольца и операции применились)
    ops_used = [(v + s) % 7 for s in range(5)]
    passport = f"Ring_Class_{v+1}__Ops_Sequence_{ops_used}"
    
    for m in range(mutations_per_variant):
        # 1% случайная погрешность (мутация) индивидуально на каждое число в ряду
        # Генерируем множители в диапазоне [0.99, 1.01]
        mutation_noise = np.random.uniform(0.99, 1.01, size=100)
        mutated_seq = base_seq * mutation_noise
        
        # Собираем строчку для Excel
        row_data = {
            "Global_Row_ID": (v * mutations_per_variant) + m + 1,
            "Ring_Class_ID": v + 1,                      # Айдишник семейства (1-28)
            "Mutation_ID": m + 1,                        # Номер мутации (1-35)
            "Passport_Formula": passport                 # Генетический паспорт
        }
        
        # Записываем 100 чисел нашего ряда в отдельные колонки
        for num_idx, val in enumerate(mutated_seq):
            row_data[f"Num_{num_idx+1}"] = val
            
        all_rows.append(row_data)

# Переводим в DataFrame и экспортируем в CSV/Excel
df = pd.DataFrame(all_rows)
df.to_csv("synthetic_rings_980_dataset.csv", index=False)

print(f" Успешно сгенерировано рядов: {df.shape[0]}")
print(f" Количество колонок (включая паспорт): {df.shape[1]}")
print(" Файл 'synthetic_rings_980_dataset.csv' готов для скармливания Мега-Атласу!")
