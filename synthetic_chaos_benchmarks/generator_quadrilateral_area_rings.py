import numpy as np
import pandas as pd

def generate_quad_area(quad_type, step_idx):
    """
    Генерирует случайный четырехугольник заданного типа 
    и возвращает его честную геометрическую площадь.
    Масштаб параметров зависит от шага ряда (step_idx).
    """
    # Базовый линейный масштаб, чтобы площади динамически развивались
    scale = (step_idx + 1) * 1.5
    
    if quad_type == "parallelogram":
        # Площадь = основание * высота
        base = np.random.uniform(5.0, 15.0) * scale
        height = np.random.uniform(4.0, 12.0) * scale
        return base * height
        
    elif quad_type == "trapezoid":
        # Площадь = ((a + b) / 2) * h
        base1 = np.random.uniform(6.0, 18.0) * scale
        base2 = np.random.uniform(4.0, 14.0) * scale
        height = np.random.uniform(5.0, 10.0) * scale
        return ((base1 + base2) / 2.0) * height
        
    elif quad_type == "rhombus":
        # Площадь = (d1 * d2) / 2 (ромб со случайными диагоналями)
        diag1 = np.random.uniform(8.0, 20.0) * scale
        diag2 = np.random.uniform(6.0, 16.0) * scale
        return (diag1 * diag2) / 2.0
        
    elif quad_type == "rectangle":
        # Площадь = длина * ширина
        length = np.random.uniform(5.0, 25.0) * scale
        width = np.random.uniform(3.0, 15.0) * scale
        return length * width
        
    return 0.0

def generate_geometry_ring_sequence(variant_idx):
    """
    Выращивает ряд из 100 чисел, где основой служат динамические площади 
    четырехугольников, пропущенные через 5 каскадных колец.
    """
    # Шаг 1: Инициализируем вектор из 100 площадей в зависимости от класса
    x = np.zeros(100, dtype=float)
    
    # 4 типа четырехугольников циклически сменяют друг друга
    quad_types = ["parallelogram", "trapezoid", "rhombus", "rectangle"]
    
    for i in range(100):
        # Выбираем тип четырехугольника на основе класса и индекса шага
        type_selector = (variant_idx + i) % 4
        chosen_type = quad_types[type_selector]
        x[i] = generate_quad_area(chosen_type, i)
        
    # Шаг 2: Прогоняем полученный геометрический профиль через 5 колец трансформаций
    for step in range(5):
        op_selector = (variant_idx + step) % 7
        
        if op_selector == 0:
            x = x / 25.0                                 # Геометрическое сжатие
        elif op_selector == 1:
            x = x * np.log(np.abs(x) + 1e-9)             # Логарифмический изгиб плоскости
        elif op_selector == 2:
            x = x + np.sin(x) * 20.0                     # Волновое кручение решетки
        elif op_selector == 3:
            x = x * 1.618                                # Масштаб Золотого Сечения (трансформация Hat/Spectre)
        elif op_selector == 4:
            # Превращаем площади в многомерные радиусы-векторы
            x = np.sign(x) * (np.abs(x) ** 1.03) 
        elif op_selector == 5:
            x = x + (x % 9) * 4.0                        # Дискретный мозаичный сдвиг
        elif op_selector == 6:
            x = x - np.cos(x) * 12.0                     # Апериодическая интерференция
            
    return x

# Сборка датасета (28 вариантов * 35 мутаций = 980 геометрических рядов)
all_geo_rows = []
total_variants = 28
mutations_per_variant = 35

for v in range(total_variants):
    # Генерируем чистую геометрию для этого класса
    base_geo_seq = generate_geometry_ring_sequence(v)
    
    # Формируем Паспорт цепочки колец
    ops_used = [(v + s) % 7 for s in range(5)]
    passport = f"Geometry_Class_{v+1}__QuadRings_{ops_used}"
    
    for m in range(mutations_per_variant):
        # 1% случайная пространственная погрешность (мутация)
        spatial_noise = np.random.uniform(0.99, 1.01, size=100)
        mutated_geo_seq = base_geo_seq * spatial_noise
        
        row_data = {
            "Global_Row_ID": (v * mutations_per_variant) + m + 1,
            "Geometry_Class_ID": v + 1,
            "Mutation_ID": m + 1,
            "Passport_Formula": passport
        }
        
        for num_idx, val in enumerate(mutated_geo_seq):
            if np.isnan(val) or np.isinf(val):
                val = 0.0
            row_data[f"Num_{num_idx+1}"] = val
            
        all_geo_rows.append(row_data)

# Экспорт в файл
df_geo = pd.DataFrame(all_rows if 'all_rows' in locals() else all_geo_rows)
df_geo.to_csv("synthetic_quad_areas_980.csv", index=False)

print(f" Геометрическая фабрика четырехугольников запущена! Создано рядов: {df_geo.shape}")
print(" Файл 'synthetic_quad_areas_980.csv' успешно собран и снабжен Паспортами структур.")
