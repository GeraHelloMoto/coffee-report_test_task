import csv
from unittest.mock import patch

import pytest

from coffee_report import load_data, MedianCoffeeReport, main, REPORTS


def test_load_data_single_file(tmp_path):
    file = tmp_path / "data.csv"
    content = [
        ["student", "date", "coffee_spent", "sleep_hours", "study_hours", "mood", "exam"],
        ["Алексей Смирнов", "2024-06-01", "450", "4.5", "12", "норм", "Математика"],
        ["Алексей Смирнов", "2024-06-02", "500", "4.0", "14", "устал", "Математика"],
        ["Дарья Петрова", "2024-06-01", "200", "7.0", "6", "отл", "Математика"],
    ]
    with open(file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(content)

    data = load_data([str(file)])
    assert data == {
        "Алексей Смирнов": [450.0, 500.0],
        "Дарья Петрова": [200.0],
    }


def test_load_data_multiple_files(tmp_path):
    file1 = tmp_path / "data1.csv"
    file2 = tmp_path / "data2.csv"
    content1 = [["student", "coffee_spent"], ["Student A", "100"], ["Student B", "200"]]
    content2 = [["student", "coffee_spent"], ["Student A", "150"], ["Student C", "300"]]
    for f, c in ((file1, content1), (file2, content2)):
        with open(f, 'w', newline='', encoding='utf-8') as out:
            writer = csv.writer(out)
            writer.writerows(c)

    data = load_data([str(file1), str(file2)])
    assert data == {
        "Student A": [100.0, 150.0],
        "Student B": [200.0],
        "Student C": [300.0],
    }


def test_load_data_missing_file():
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        load_data(["nonexistent.csv"])


def test_load_data_missing_column(tmp_path):
    file = tmp_path / "bad.csv"
    with open(file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["student", "date"])
        writer.writerow(["Alex", "2024-01-01"])
    with pytest.raises(ValueError, match="не содержит колонку 'coffee_spent'"):
        load_data([str(file)])


def test_load_data_invalid_coffee(tmp_path):
    file = tmp_path / "invalid.csv"
    with open(file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["student", "coffee_spent"])
        writer.writerow(["Alex", "not a number"])
        writer.writerow(["Bob", "10"])
    data = load_data([str(file)])
    assert data == {"Bob": [10.0]}


def test_median_report():
    data = {
        "Student A": [10, 20, 30],
        "Student B": [5, 15],
        "Student C": [100],
    }
    report = MedianCoffeeReport()
    result = report.generate(data)
    expected = [("Student C", 100.0), ("Student A", 20.0), ("Student B", 10.0)]
    assert result == expected


def test_median_report_empty_values():
    data = {
        "Student A": [],
        "Student B": [10],
    }
    report = MedianCoffeeReport()
    result = report.generate(data)
    assert result == [("Student B", 10.0)]


def test_main_unknown_report(capsys):
    with patch('sys.argv', ['script.py', '--files', 'dummy.csv', '--report', 'unknown']):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "отчёт 'unknown' не найден" in captured.err


def test_main_missing_files(capsys):
    with patch('sys.argv', ['script.py', '--files', 'nonexistent.csv', '--report', 'median-coffee']):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "Файл не найден" in captured.err


def test_main_success(tmp_path, capsys):
    file = tmp_path / "data.csv"
    with open(file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["student", "coffee_spent"])
        writer.writerow(["Alex", "100"])
        writer.writerow(["Alex", "200"])
        writer.writerow(["Bob", "300"])
    with patch('sys.argv', ['script.py', '--files', str(file), '--report', 'median-coffee']):
        main()
        captured = capsys.readouterr()
        assert "Alex" in captured.out
        assert "Bob" in captured.out
        lines = captured.out.split('\n')
        
        found_bob = any("Bob" in line and "300" in line for line in lines)
        found_alex = any("Alex" in line and "150" in line for line in lines)
        assert found_bob, "Строка с Bob и 300 не найдена"
        assert found_alex, "Строка с Alex и 150 не найдена"