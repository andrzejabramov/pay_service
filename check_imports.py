#!/usr/bin/env python3
"""
Скрипт для проверки всех импортов в проекте alpha_hook.
Находит синтаксические ошибки, битые импорты и циклические зависимости.

Использование:
    python check_imports.py

Или с указанием пути:
    python check_imports.py --path ./alpha_hook/src
"""

import sys
import os
import argparse
from pathlib import Path
from importlib import util
from typing import List, Tuple, Optional
import traceback


class ImportChecker:
    """Проверка импортов в Python-проекте"""

    def __init__(self, project_path: str, exclude_dirs: List[str] = None):
        self.project_path = Path(project_path)
        self.exclude_dirs = exclude_dirs or ['__pycache__', '.venv', 'venv', 'node_modules', '.git']
        self.errors: List[Tuple[str, str]] = []
        self.warnings: List[Tuple[str, str]] = []
        self.checked_files: List[str] = []

    def find_python_files(self) -> List[Path]:
        """Найти все .py файлы в проекте"""
        files = []
        for py_file in self.project_path.rglob('*.py'):
            # Исключить директории
            if any(exclude in str(py_file) for exclude in self.exclude_dirs):
                continue
            files.append(py_file)
        return sorted(files)

    def check_syntax(self, file_path: Path) -> Optional[str]:
        """Проверить синтаксис файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(file_path), 'exec')
            return None
        except SyntaxError as e:
            return f"SyntaxError: {e.msg} (line {e.lineno})"
        except Exception as e:
            return f"Error: {str(e)}"

    def check_import(self, file_path: Path) -> Optional[str]:
        """Попытаться импортировать модуль"""
        try:
            # Получить имя модуля относительно project_path
            rel_path = file_path.relative_to(self.project_path.parent)
            module_name = str(rel_path).replace('/', '.').replace('\\', '.').replace('.py', '')

            # Загрузить модуль
            spec = util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

            return None
        except ImportError as e:
            return f"ImportError: {str(e)}"
        except ModuleNotFoundError as e:
            return f"ModuleNotFoundError: {str(e)}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"

    def check_all(self) -> bool:
        """Проверить все файлы в проекте"""

        src_path = self.project_path.resolve()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        print(f"🔍 Проверка импортов в: {self.project_path}")
        print(f"📁 sys.path: {src_path}")
        print("=" * 60)

        py_files = self.find_python_files()
        print(f"📁 Найдено файлов: {len(py_files)}\n")

        for file_path in py_files:
            rel_path = file_path.relative_to(self.project_path)
            print(f"⏳ Проверка: {rel_path}", end=" ... ")

            # 1. Проверка синтаксиса
            syntax_error = self.check_syntax(file_path)
            if syntax_error:
                print(f"❌ {syntax_error}")
                self.errors.append((str(rel_path), syntax_error))
                continue

            # 2. Проверка импорта
            import_error = self.check_import(file_path)
            if import_error:
                print(f"❌ {import_error}")
                self.errors.append((str(rel_path), import_error))
            else:
                print("✅ OK")
                self.checked_files.append(str(rel_path))

        # Отчёт
        self.print_report()

        return len(self.errors) == 0

    def print_report(self):
        """Вывести отчёт о проверке"""
        print("\n" + "=" * 60)
        print("📊 ОТЧЁТ")
        print("=" * 60)
        print(f"✅ Успешно проверено: {len(self.checked_files)} файлов")
        print(f"❌ Ошибок: {len(self.errors)}")
        print(f"⚠️  Предупреждений: {len(self.warnings)}")

        if self.errors:
            print("\n🔴 ОШИБКИ:")
            for file_path, error in self.errors:
                print(f"  • {file_path}: {error}")

        if self.warnings:
            print("\n🟡 ПРЕДУПРЕЖДЕНИЯ:")
            for file_path, warning in self.warnings:
                print(f"  • {file_path}: {warning}")

        print("\n" + "=" * 60)
        if self.errors:
            print("❌ ПРОВЕРКА НЕ ПРОЙДЕНА")
            return 1
        else:
            print("✅ ВСЕ ИМПОРТЫ РАБОТАЮТ")
            return 0


def main():
    parser = argparse.ArgumentParser(description='Проверка импортов в проекте')
    parser.add_argument('--path', default='./alpha_hook/src', help='Путь к исходному коду')
    parser.add_argument('--exclude', nargs='+', default=['__pycache__', '.venv'], help='Исключить директории')

    args = parser.parse_args()

    checker = ImportChecker(args.path, args.exclude)
    success = checker.check_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()