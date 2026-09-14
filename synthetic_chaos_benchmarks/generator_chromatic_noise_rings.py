import numpy as np
import pandas as pd

def generate_colored_noise(length, noise_type):
    """
    Генерирует базовые цветные шумы через спектральное окрашивание (1/f^beta)
    или рекуррентные алгоритмы.
    """
    if noise_type == "white":
        return np.random.normal(0, 1, length)
        
    elif noise_type == "pink":
        # Розовый шум (1/f): генерируем через БПФ
        uneven = length % 2
        X_white = np.random.normal(0, 1, length)
        X_fourier = np.fft.rfft(X_white)
        # Масштабируем амплитуды по закону 1/sqrt(f)
        frequencies = np.fft.rfftfreq(length)
        frequencies[0] = frequencies[1]  # защита от деления на 0
        X_fourier = X_fourier / np.sqrt(frequencies)
        result = np.fft.irfft(X_fourier, length)
        return result / np.std(result)
        
    elif noise_type == "red":
        # Красный/Броуновский шум (1/f^2): кумулятивная сумма (случайное блуждание)
        return np.cumsum(np.random.normal(0, 1, length))
        
    elif noise_type == "blue":
        # Синий шум (f): дифференциал белого шума (резкие скачки высоких частот)
        white = np.random.normal(0, 1, length + 1)
        result = np.diff(white)
        return result / np.std(result)
        
    elif noise_type == "black":
        # Черный шум: затишье + редкие катастрофы (интенсивные всплески)
        base = np.random.normal(0, 0.1, length)
        # Вшиваем 1-2 случайных тяжелых "катастрофических" удара
        spike_indices = np.random.choice(length, size=np.random.randint(1, 3), replace=False)
        for idx in spike_indices:
            base[idx] += np.random.choice([-1, 1]) * np.random.uniform(15.0, 30.0)
        return base
        
    return np.zeros(length)

def generate_chromatic_ring_sequence(variant_idx):
    """
    Выращивает ряд из 100 чисел через 5 каскадных колец, 
    где математические законы вложены в спектральные цветные шумы.
    """
    x = np.arange(1, 101, dtype=float)
    
    # 7 Хроматических Математических Колец
    for step in range(5):
        op_selector = (variant_idx + step) % 7
        
        if op_selector == 0:
            # Кольцо 0: Плавный Красный тренд (Память системы)
            x = x + generate_colored_noise(100, "red") * 5.0
        elif op_selector == 1:
            # Кольцо 1: Масштабирование + Натуральный Логарифм
            x = (x / 20.0) * np.log(np.abs(x) + 1e-9)
        elif op_selector == 2:
            # Кольцо 2: Синий высокочастотный шум (Взрывная пульсация)
            x = x + generate_colored_noise(100, "blue") * 4.0
        elif op_selector == 3:
            # Кольцо 3: Природный Розовый резонанс
            x = x * (1.0 + generate_colored_noise(100, "pink") * 0.2)
        elif op_selector == 4:
            # Кольцо 4: Черный шум (Вшивание критического сбоя/катастрофы)
            x = x + generate_colored_noise(100, "black")
        elif op_selector == 5:
            # Кольцо 5: Нелинейное степенное сжатие Золотого Сечения
            x = np.sign(x) * (np.abs(x) ** 1.05) * 1.618
        elif op_selector == 6:
            # Кольцо 6: Модулярный сдвиг, закрученный в белый хаос
            x = x + (x % 7) * 2.0 + generate_colored_noise(100, "white") * 1.5
            
    return x

# Сборка мега-массива данных (28 вариантов * 35 мутаций = 980 хроматических рядов)
all_chromatic_rows = []
total_variants = 28
mutations_per_variant = 35

for v in range(total_variants):
    # Генерируем чистое хроматическое ядро класса
    base_chromatic_seq = generate_chromatic_ring_sequence(v)
    
    # Формируем Паспорт цепочки колец
    ops_used = [(v + s) % 7 for s in range(5)]
    passport = f"Chromatic_Class_{v+1}__Rings_{ops_used}"
    
    for m in range(mutations_per_variant):
        # 1% финальная мутация (микро-деформация структуры)
        final_mutation = np.random.uniform(0.99, 1.01, size=100)
        mutated_seq = base_chromatic_seq * final_mutation
        
        row_data = {
            "Global_Row_ID": (v * mutations_per_variant) + m + 1,
            "Chromatic_Class_ID": v + 1,
            "Mutation_ID": m + 1,
            "Passport_Formula": passport
        }
        
        for num_idx, val in enumerate(mutated_seq):
            if np.isnan(val) or np.isinf(val):
                val = 0.0
            row_data[f"Num_{num_idx+1}"] = val
            
        all_chromatic_rows.append(row_data)

# Экспорт в датасет
df_chromatic = pd.DataFrame(all_chromatic_rows)
df_chromatic.to_csv("synthetic_chromatic_noises_980.csv", index=False)

print(f" Хроматическая фабрика завершила расчет! Создано рядов: {df_chromatic.shape}")
print(" Файл 'synthetic_chromatic_noises_980.csv' успешно собран и готов к тесту.")
