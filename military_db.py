#!/usr/bin/env python3
"""Работа с базой данных военнослужащих в виде pandas DataFrame с двухуровневой структурой столбцов: общая категория -> подкатегория.

Функции:
- load_default_data(): создает DataFrame с демонстрационными данными.
- filter_data(df, **criteria): выборка по значениям (боевая часть, ФИО, должность).
- plot_mortgage(df): строит график распределения ипотеки (да/нет).
- main(): пример использования.
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

def load_default_data() -> pd.DataFrame:
    data = [
        {
            ('Служба','Боевая часть'): 'Первый батальон',
            ('Персональные данные','ФИО'): 'Иванов Иван Иванович',
            ('Служба','Должность'): 'Сержант',
            ('Персональные данные','Дата рождения'): '1990-05-20',
            ('Финансы','Ипотека'): 'Да',
        },
        {
            ('Служба','Боевая часть'): 'Второй батальон',
            ('Персональные данные','ФИО'): 'Петров Петр Петрович',
            ('Служба','Должность'): 'Лейтенант',
            ('Персональные данные','Дата рождения'): '1988-11-02',
            ('Финансы','Ипотека'): 'Нет',
        },
        {
            ('Служба','Боевая часть'): 'Первый батальон',
            ('Персональные данные','ФИО'): 'Сидоров Сидор Сидорович',
            ('Служба','Должность'): 'Капитан',
            ('Персональные данные','Дата рождения'): '1985-03-15',
            ('Финансы','Ипотека'): 'Да',
        },
    ]
    df = pd.DataFrame(data)
    df[('Персональные данные','Дата рождения')] = pd.to_datetime(df[('Персональные данные','Дата рождения')])
    today = pd.Timestamp.today().normalize()
    df[('Персональные данные','Возраст')] = (today - df[('Персональные данные','Дата рождения')]).dt.days // 365
    return df

def filter_data(df: pd.DataFrame, **criteria: Any) -> pd.DataFrame:
    """
    Фильтрация по указанным значениям:
    filter_data(df, combat_unit='Первый батальон', position='Сержант')
    """
    mapping: Dict[str, tuple] = {
        'combat_unit': ('Служба','Боевая часть'),
        'full_name': ('Персональные данные','ФИО'),
        'position': ('Служба','Должность'),
        'mortgage': ('Финансы','Ипотека'),
    }
    mask = pd.Series([True] * len(df))
    for key, value in criteria.items():
        col = mapping.get(key)
        if col:
            mask &= df[col] == value
    return df[mask]

def plot_mortgage(df: pd.DataFrame) -> None:
    counts = df[('Финансы','Ипотека')].value_counts()
    counts.plot(kind='bar', title='Наличие ипотеки')
    plt.xlabel('Ипотека')
    plt.ylabel('Количество военнослужащих')
    plt.tight_layout()
    plt.savefig('mortgage_plot.png')

def main() -> None:
    df = load_default_data()
    print('Полная таблица:')
    print(df.to_string(index=False))

    print('\nПример выборки (Первый батальон):')
    print(filter_data(df, combat_unit='Первый батальон').to_string(index=False))

    plot_mortgage(df)
    print('\nГрафик сохранён в mortgage_plot.png')

if __name__ == '__main__':
    main()
