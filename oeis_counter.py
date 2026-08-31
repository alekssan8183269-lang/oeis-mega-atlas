import gzip
import os

INPUT_STRIPPED = "stripped.gz"
INPUT_NAMES = "names.gz"

def count_rows(file_name, file_type):
    if not os.path.exists(file_name):
        print(f"❌ Файл {file_name} не найден в папке!")
        return 0
        
    print(f"⏳ Считаем строки в {file_name}...")
    count = 0
    with gzip.open(file_name, 'rt', encoding='utf-8') as f:
        for line in f:
            # Пропускаем комментарии (строки, которые начинаются с #)
            if line.startswith('#') or not line.strip():
                continue
            count += 1
    print(f"✅ В файле {file_name} найдено {count} реальных {file_type}.")
    return count

if __name__ == "__main__":
    print("🚀 Запуск счетчика Вселенной OEIS...")
    print("="*50)
    
    total_names = count_rows(INPUT_NAMES, "названий")
    total_seqs = count_rows(INPUT_STRIPPED, "числовых рядов")
    
    print("="*50)
    print(f"👑 Итог: Твой компьютер готов переварить {total_seqs} мировых математических законов!")
