import os
import sys
import glob

def read_file_safe(path):
    """Читает файл, возвращает содержимое или ошибку."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[ОШИБКА ЧТЕНИЯ: {e}]"

def main():
    if len(sys.argv) < 2:
        print("Использование: python context_agent.py <шаблон1> <шаблон2> ...")
        print("Пример: python context_agent.py 'docker-compose.yml' '.env' 'services/*/Dockerfile'")
        return

    patterns = sys.argv[1:]
    all_files = set()

    # Собираем все файлы по шаблонам
    for pattern in patterns:
        if os.path.isfile(pattern):
            all_files.add(pattern)
        else:
            matched = glob.glob(pattern, recursive=True)
            all_files.update(matched)

    if not all_files:
        print("Ни один файл не найден по указанным шаблонам.")
        return

    # Выводим содержимое в форматированном виде
    output_lines = []
    for file_path in sorted(all_files):
        output_lines.append(f"\n=== {file_path} ===")
        content = read_file_safe(file_path)
        output_lines.append(content)

    result = "\n".join(output_lines)
    print(result)

    # Опционально: сохранить в файл
    save = input("\nСохранить вывод в context1.txt? (y/n): ").strip().lower()
    if save == 'y':
        with open("../docs/context1.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("✅ Сохранено в context1.txt")

if __name__ == "__main__":
    main()