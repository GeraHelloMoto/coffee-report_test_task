import argparse
import csv
import sys
from statistics import median
from typing import Dict, List, Tuple

from tabulate import tabulate


class Report:
    

    def generate(self, data: Dict[str, List[float]]) -> List[Tuple[str, float]]:
        
        raise NotImplementedError


class MedianCoffeeReport(Report):
    

    def generate(self, data: Dict[str, List[float]]) -> List[Tuple[str, float]]:
        result = []
        for student, values in data.items():
            if values:
                med = median(values)
                result.append((student, med))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result



REPORTS = {
    "median-coffee": MedianCoffeeReport(),
}


def load_data(files: List[str]) -> Dict[str, List[float]]:
    
    data = {}
    for file_path in files:
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if 'coffee_spent' not in reader.fieldnames:
                    raise ValueError(
                        f"Файл {file_path} не содержит колонку 'coffee_spent'"
                    )
                for row in reader:
                    student = row.get('student', '').strip()
                    if not student:
                        continue
                    try:
                        coffee = float(row['coffee_spent'])
                    except ValueError:
                        
                        continue
                    data.setdefault(student, []).append(coffee)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении файла {file_path}: {e}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Генерация отчёта о потреблении кофе"
    )
    parser.add_argument(
        "--files", nargs="+", required=True,
        help="Пути к CSV-файлам с данными"
    )
    parser.add_argument(
        "--report", required=True,
        help="Название отчёта (например, median-coffee)"
    )
    args = parser.parse_args()

    if args.report not in REPORTS:
        print(
            f"Ошибка: отчёт '{args.report}' не найден. "
            f"Доступные отчёты: {', '.join(REPORTS.keys())}",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        data = load_data(args.files)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    report = REPORTS[args.report]
    table_data = report.generate(data)

    headers = ["Студент", "Медианная сумма трат на кофе"]
    print(tabulate(table_data, headers=headers, tablefmt="pretty"))


if __name__ == "__main__":
    main()