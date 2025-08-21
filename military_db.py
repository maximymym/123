#!/usr/bin/env python3
"""Интерактивная работа с базой данных военнослужащих.

Используется pandas для хранения информации в DataFrame с
двухуровневой структурой столбцов (категория -> подкатегория).
Для красивого вывода и простого взаимодействия применяется библиотека
`rich`.

Возможности:
- добавление столбцов (категория/подкатегория);
- добавление записей;
- фильтрация по произвольному столбцу;
- построение графиков распределения значений.

Запуск без аргументов открывает интерактивное меню.
Опция ``--demo`` демонстрирует работу без ввода пользователя.
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import pandas as pd
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


class MilitaryDB:
    """Класс-обертка над DataFrame с удобными методами."""

    def __init__(self) -> None:
        self.df = load_default_data()

    # ---- Работа со столбцами и строками ---------------------------------
    def add_column(self, category: str, subcategory: str, default: Any = None) -> None:
        """Добавить столбец в виде пары (категория, подкатегория)."""
        self.df[(category, subcategory)] = default

    def add_record(self, data: Dict[Tuple[str, str], Any]) -> None:
        """Добавить новую запись (строку) в таблицу."""
        self.df = pd.concat([self.df, pd.DataFrame([data])], ignore_index=True)

    # ---- Отображение -----------------------------------------------------
    def display(self, df: pd.DataFrame | None = None) -> None:
        """Показать таблицу в виде красивой консольной таблицы."""
        target = df if df is not None else self.df
        table = Table(show_lines=True)
        for cat, sub in target.columns:
            table.add_column(f"{cat}\n{sub}")
        for _, row in target.iterrows():
            table.add_row(*["" if pd.isna(x) else str(x) for x in row])
        console.print(table)

    # ---- Фильтрация ------------------------------------------------------
    def filter_interactive(self) -> None:
        """Фильтрация по столбцу с вводом параметров."""
        cat = Prompt.ask("Категория")
        sub = Prompt.ask("Подкатегория")
        value = Prompt.ask("Значение")
        col = (cat, sub)
        if col in self.df.columns:
            filtered = self.df[self.df[col] == value]
            self.display(filtered)
        else:
            console.print("Такого столбца нет", style="red")

    # ---- Построение графиков --------------------------------------------
    def plot_counts(self, category: str, subcategory: str, filename: str = "plot.png") -> None:
        """Построить график распределения значений столбца."""
        col = (category, subcategory)
        if col not in self.df.columns:
            console.print("Такого столбца нет", style="red")
            return
        counts = self.df[col].value_counts()
        counts.plot(kind="bar", title=f"{category} / {subcategory}")
        plt.tight_layout()
        plt.savefig(filename)
        console.print(f"График сохранён в {filename}")

    def plot_interactive(self) -> None:
        cat = Prompt.ask("Категория для графика")
        sub = Prompt.ask("Подкатегория для графика")
        self.plot_counts(cat, sub)

    # ---- Интерактивное добавление ---------------------------------------
    def add_column_interactive(self) -> None:
        cat = Prompt.ask("Новая категория")
        sub = Prompt.ask("Новая подкатегория")
        default = Prompt.ask("Значение по умолчанию", default="")
        self.add_column(cat, sub, default or None)

    def add_record_interactive(self) -> None:
        data: Dict[Tuple[str, str], Any] = {}
        for cat, sub in self.df.columns:
            value = Prompt.ask(f"{cat} / {sub}", default="")
            data[(cat, sub)] = value or None
        self.add_record(data)

    # ---- Главное меню ----------------------------------------------------
    def menu(self) -> None:
        actions = {
            "1": ("Показать таблицу", self.display),
            "2": ("Добавить столбец", self.add_column_interactive),
            "3": ("Добавить запись", self.add_record_interactive),
            "4": ("Фильтр по столбцу", self.filter_interactive),
            "5": ("Построить график", self.plot_interactive),
            "0": ("Выход", None),
        }
        while True:
            console.print("\n[bold]Меню[/bold]")
            for key, (title, _) in actions.items():
                console.print(f"{key}. {title}")
            choice = Prompt.ask("Выберите пункт", choices=list(actions.keys()))
            if choice == "0":
                break
            action = actions[choice][1]
            if action:
                action()


# ---- Вспомогательные функции -------------------------------------------

def load_default_data() -> pd.DataFrame:
    data = [
        {
            ("Служба", "Боевая часть"): "Первый батальон",
            ("Персональные данные", "ФИО"): "Иванов Иван Иванович",
            ("Служба", "Должность"): "Сержант",
            ("Персональные данные", "Дата рождения"): "1990-05-20",
            ("Финансы", "Ипотека"): "Да",
        },
        {
            ("Служба", "Боевая часть"): "Второй батальон",
            ("Персональные данные", "ФИО"): "Петров Петр Петрович",
            ("Служба", "Должность"): "Лейтенант",
            ("Персональные данные", "Дата рождения"): "1988-11-02",
            ("Финансы", "Ипотека"): "Нет",
        },
        {
            ("Служба", "Боевая часть"): "Первый батальон",
            ("Персональные данные", "ФИО"): "Сидоров Сидор Сидорович",
            ("Служба", "Должность"): "Капитан",
            ("Персональные данные", "Дата рождения"): "1985-03-15",
            ("Финансы", "Ипотека"): "Да",
        },
    ]
    df = pd.DataFrame(data)
    df[("Персональные данные", "Дата рождения")] = pd.to_datetime(
        df[("Персональные данные", "Дата рождения")]
    )
    today = pd.Timestamp.today().normalize()
    df[("Персональные данные", "Возраст")] = (
        today - df[("Персональные данные", "Дата рождения")]
    ).dt.days // 365
    return df


def demo() -> None:
    """Небольшая демонстрация возможностей без ввода пользователя."""
    db = MilitaryDB()
    console.print("[bold]Демонстрация базы данных[/bold]")
    db.display()
    console.print("\nДобавление столбца 'Статус / Контракт'")
    db.add_column("Статус", "Контракт", "Да")
    console.print("Добавление записи")
    db.add_record(
        {
            ("Служба", "Боевая часть"): "Третий батальон",
            ("Персональные данные", "ФИО"): "Кузнецов Константин Константинович",
            ("Служба", "Должность"): "Рядовой",
            ("Персональные данные", "Дата рождения"): "1995-07-01",
            ("Финансы", "Ипотека"): "Нет",
            ("Статус", "Контракт"): "Нет",
        }
    )
    db.display()
    db.plot_counts("Финансы", "Ипотека", filename="mortgage_plot.png")


# ---- Точка входа --------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Интерфейс для базы данных военнослужащих")
    parser.add_argument("--demo", action="store_true", help="запустить демонстрацию и выйти")
    args = parser.parse_args()
    if args.demo:
        demo()
    else:
        db = MilitaryDB()
        db.menu()


if __name__ == "__main__":
    main()
