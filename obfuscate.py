#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

KB_DIR = Path("knowledge_base")
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 1. МИНИМАЛИСТИЧНЫЙ СЛОВАРЬ ЗАМЕН БЕЗ ПОВТОРОВ И ПЕРЕСЕЧЕНИЙ
terms_map = {
    # Персонажи (в начальной форме)
    "Наруто Узумаки": "Княжич Мирослав",
    "Саске Учиха": "Воевода Святослав",
    "Сакура Харуно": "Целительница Рада",
    "Хатаке Какаши": "Наставник Добрыня",
    "Итачи Учиха": "Изгнанник Лютобор",
    "Минато Намиказе": "Светлый Князь Всеслав",
    "Тобирама Сенджу": "Воевода Изяслав",
    "Хаширама Сенджу": "Древний Князь Ярослав",
    "Мадара Учиха": "Князь-Отступник Твердислав",
    "Обито Учиха": "Мятежник Ратибор",
    "Хината Хьюга": "Княжна Лада",
    "Неджи Хьюга": "Витязь Пересвет",
    "Шикамару Нара": "Советник Велимудр",
    "Джирайя": "Старец Всеволод",
    "Цунаде": "Княгиня Ольга",
    "Орочимару": "Колдун Чернобог",
    "Нагато": "Старейшина Борислав",
    "Рок Ли": "Ратник Удалец",
    "Гаара": "Страж Гор Милорад",
    "Курама": "Дух Огненного Зверя",

    # Сущности, организации и понятия
    "Конохагакуре": "Княжество Velvet",
    "Акацуки": "Тайный Орден Изгоев",
    "Клан Учиха": "Древний Род Хранителей Ока",
    "Риннеган": "Дар Высшего Видения",
    "Шаринган": "Око Прорицания",
    "Бьякуган": "Взор Сквозь Стены",
    "Хвостатый Зверь": "Древний Хранитель Энергии",
    "Десятихвостый": "Первородный Хаос",
    "Хокаге": "Великий Князь",
    "Кунай": "охотничий кинжал",
    "Чакра": "Внутренняя Энергия (Жива)",
    "Расенган": "Вихревой Удар",
    "Чидори": "Громовой Клинок",
    "Техника Призыва": "Призыв Лесных Духов",
    "Техника Летящего Бога Грома": "Искусство Мгновенного Переноса",
    "Режим Мудреца": "Слияние с Природой",
    "Восемь Врат": "Восемь Пределов Тела",
    "Эдо Тенсей": "Заклятие Воскрешения Предков",
    "Техника Теневого Клонирования": "Искусство Множественных Отражений",
    "Гендзюцу": "Магия Наслания Иллюзий",

    # События
    "Разрушение Конохи": "Осада Княжества Velvet",
    "Экзамены на Чуунина": "Испытание Молодых Ратников",
    "Четвёртая Мировая Война Шиноби": "Великая Война За Земли Содружества",
    "Нападение Девятихвостого Демона-Лиса": "Прорыв Огненного Зверя",
    "Нападение Пейна": "Разорение Центральной Обители",
    "Бесконечное Цукуёми": "Вечный Сон Семи Земель",
    "Долина Завершения": "Пограничный Рубеж Великой Реки",
    "Миссия Возвращения Саске": "Поход За Беглым Воеводой",
    "Собрание Пяти Каге": "Совет Великих Князей"
}

# Записываем чистый словарь в отдельный файл data/terms_map.json
with open(DATA_DIR / "terms_map.json", "w", encoding="utf-8") as f:
    json.dump(terms_map, f, ensure_ascii=False, indent=2)

print("Запуск тотальной динамической обфускации базы знаний...")
processed = 0

# Поддерживаем обработку как .txt (исходных), так и уже созданных .md файлов
for ext in ["*.txt", "*.md"]:
    for out_path in KB_DIR.glob(ext):
        text = out_path.read_text(encoding="utf-8")

        # Удаляем строку со ссылкой на оригинал (Source: ...)
        text = re.sub(r'^Source:.*\n?', '', text, flags=re.MULTILINE)

        # 1. Заменяем полные имена и монолитные термины из словаря
        for original in sorted(terms_map.keys(), key=len, reverse=True):
            text = text.replace(original, terms_map[original])
            text = text.replace(original.lower(), terms_map[original].lower())

        # 2. ДИНАМИЧЕСКАЯ ИНТЕЛЛЕКТУАЛЬНАЯ ЗАЧИСТКА ХВОСТОВ И ПАДЕЖЕЙ
        # Вычищаем любые упоминания "Коноха" во всех формах
        text = re.sub(r'Конох[а-яА-Я]*', 'Княжество Velvet', text)
        text = re.sub(r'конох[а-яА-Я]*', 'Княжество Velvet', text)

        # Унифицируем все формы слова "деревня"
        text = re.sub(r'деревн[а-яА-Я]*', 'княжество', text)
        text = re.sub(r'Деревн[а-яА-Я]*', 'Княжество', text)

        # ИСПРАВЛЕНИЕ: Динамическая замена Гаара во всех падежах (Гаара, Гаару, Гааре, Гаарой)
        text = re.sub(r'Гаар[а-яА-Я]*', 'Страж Гор Милорад', text)
        text = re.sub(r'гаар[а-яА-Я]*', 'Страж Гор Милорад', text)

        # ИСПРАВЛЕНИЕ: Выжигание Шукаку во всех падежах
        text = re.sub(r'Шукаку[а-яА-Я]*', 'Песчаный Дух Резерва', text)
        text = re.sub(r'шукаку[а-яА-Я]*', 'Песчаный Дух Резерва', text)

        # Заменяем остальные одиночные имена без накладок
        text = re.sub(r'Наруто[а-яА-Я]*', 'Мирослав', text, flags=re.IGNORECASE)
        text = re.sub(r'Саске[а-яА-Я]*', 'Святослав', text, flags=re.IGNORECASE)
        text = re.sub(r'Сакур[а-яА-Я]*', 'Рада', text, flags=re.IGNORECASE)
        text = re.sub(r'Какаши[а-яА-Я]*', 'Добрыня', text, flags=re.IGNORECASE)
        text = re.sub(r'Итачи[а-яА-Я]*', 'Лютобор', text, flags=re.IGNORECASE)
        text = re.sub(r'Мадар[а-яА-Я]*', 'Твердислав', text, flags=re.IGNORECASE)
        text = re.sub(r'Обито[а-яА-Я]*', 'Ратибор', text, flags=re.IGNORECASE)
        text = re.sub(r'Хинат[а-яА-Я]*', 'Лада', text, flags=re.IGNORECASE)
        text = re.sub(r'Неджи[а-яА-Я]*', 'Пересвет', text, flags=re.IGNORECASE)
        text = re.sub(r'Шикамару[а-яА-Я]*', 'Велимудр', text, flags=re.IGNORECASE)
        text = re.sub(r'Джирай[а-яА-Я]*', 'Всеволод', text, flags=re.IGNORECASE)
        text = re.sub(r'Орочимару[а-яА-Я]*', 'Чернобог', text, flags=re.IGNORECASE)

        # Стираем лорные титулы лидеров
        text = re.sub(r'[а-яА-Я]*кагэ[а-яА-Я]*', 'Великий Князь', text, flags=re.IGNORECASE)
        text = re.sub(r'[а-яА-Я]*каге[а-яА-Я]*', 'Великий Князь', text, flags=re.IGNORECASE)

        # Унифицируем общие специфичные слова лора фандома
        text = re.sub(r'шиноби', 'витязь', text, flags=re.IGNORECASE)
        text = re.sub(r'ниндзя', 'воин', text, flags=re.IGNORECASE)
        text = re.sub(r'куноичи', 'воительница', text, flags=re.IGNORECASE)
        text = re.sub(r'сюрикен[а-я]*', 'метательный клинок', text, flags=re.IGNORECASE)
        text = re.sub(r'дзинчуурики[а-я]*', 'хранитель духа зверя', text, flags=re.IGNORECASE)
        text = re.sub(r'джинчуурики[а-я]*', 'хранитель духа зверя', text, flags=re.IGNORECASE)

        # Фамилии и кланы
        text = re.sub(r"Учих[а-яА-Я]*", "Хранителей Ока", text, flags=re.IGNORECASE)
        text = re.sub(r"Узумак[а-яА-Я]*", "рода Мирослава", text, flags=re.IGNORECASE)
        text = re.sub(r"Сендж[а-яА-Я]*", "рода Ярослава", text, flags=re.IGNORECASE)
        text = re.sub(r"Хьюг[а-яА-Я]*", "рода Лады", text, flags=re.IGNORECASE)
        text = re.sub(r"Харун[а-яА-Я]*", "рода Рады", text, flags=re.IGNORECASE)
        text = re.sub(r"Намиказ[а-яА-Я]*", "рода Всеслава", text, flags=re.IGNORECASE)

        # Пропущенные персонажи
        text = re.sub(r"Цунад[а-яА-Я]*", "Ольга", text, flags=re.IGNORECASE)
        text = re.sub(r"Нагат[а-яА-Я]*", "Борислав", text, flags=re.IGNORECASE)
        text = re.sub(r"Гаар[а-яА-Я]*", "Милорад", text, flags=re.IGNORECASE)
        text = re.sub(r"Курам[а-яА-Я]*", "Огненный Зверь", text, flags=re.IGNORECASE)
        text = re.sub(r"Пейн[а-яА-Я]*", "Вестник Боли", text, flags=re.IGNORECASE)
        text = re.sub(r"Данз[а-яА-Я]*", "Советник Тень", text, flags=re.IGNORECASE)
        text = re.sub(r"Хирузен[а-яА-Я]*", "Старый Князь", text, flags=re.IGNORECASE)
        text = re.sub(r"Кабут[а-яА-Я]*", "Лекарь-Отступник", text, flags=re.IGNORECASE)

        # Деревни, страны и техники
        text = re.sub(r"[а-яА-Я]*гакур[а-яА-Я]*", "соседнее княжество", text, flags=re.IGNORECASE)
        text = re.sub(r"[а-яА-Я]*дзюц[а-яА-Я]*", "чародейство", text, flags=re.IGNORECASE)
        text = re.sub(r"Сусано[а-яА-Я]*", "Призрачный Витязь", text, flags=re.IGNORECASE)
        text = re.sub(r"Аматерас[а-яА-Я]*", "Черное Пламя", text, flags=re.IGNORECASE)
        text = re.sub(r"Цукуём[а-яА-Я]*", "Лунный Сон", text, flags=re.IGNORECASE)
        text = re.sub(r"Кьюб[а-яА-Я]*", "Огненный Зверь", text, flags=re.IGNORECASE)


        # Удаляем мусорные скобки с японскими переводами
        text = re.sub(r'\(\s*,\s*[^)]+\)', '', text)
        text = re.sub(r'досл\.[^)]+', '', text)

       # Переводим очищенное имя файла (заменяем термины и в названии файла!)
        new_stem = out_path.stem
        for original in sorted(terms_map.keys(), key=len, reverse=True):
            orig_slug = re.sub(r"[^\w]+", "_", original.lower()).strip("_")
            repl_slug = re.sub(r"[^\w]+", "_", terms_map[original].lower()).strip("_")
            new_stem = new_stem.replace(orig_slug, repl_slug)

        new_path = out_path.with_name(f"{new_stem}.md")
        new_path.write_text(text, encoding="utf-8")

        # Удаляем старый файл, если имя или расширение изменилось
        if out_path != new_path:
            out_path.unlink()

        print(f"[Успешно] {out_path.name} -> {new_path.name}")
        processed += 1

print(f"\n[УСПЕХ] Обфускация завершена! Пропущенные слова выжжены. Файлов обработано: {processed}.")
