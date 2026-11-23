#!/usr/bin/env python3
"""Download and clean Russian Narutopedia entity pages into knowledge_base/."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://naruto.fandom.com/ru/api.php"
USER_AGENT = "Mozilla/5.0 (compatible; NarutopediaKBBuilder/1.0; +https://example.com/bot)"
OUT_DIR = Path("knowledge_base")

ENTITIES = {
    "characters": [
        "Наруто Узумаки",
        "Саске Учиха",
        "Сакура Харуно",
        "Хатаке Какаши",
        "Итачи Учиха",
        "Джирайя",
        "Цунаде",
        "Орочимару",
        "Мадара Учиха",
        "Хаширама Сенджу",
        "Тобирама Сенджу",
        "Минато Намиказе",
        "Обито Учиха",
        "Нагато",
        "Хината Хьюга",
        "Неджи Хьюга",
        "Рок Ли",
        "Гаара",
        "Шикамару Нара",
        "Курама",
    ],
    "objects_and_orgs": [
        "Акацуки",
        "Конохагакуре",
        "Риннеган",
        "Шаринган",
        "Бьякуган",
        "Хвостатый Зверь",
        "Десятихвостый",
        "Клан Учиха",
        "Хокаге",
        "Кунай",
    ],
    "technologies": [
        "Чакра",
        "Расенган",
        "Чидори",
        "Техника Призыва",
        "Техника Летящего Бога Грома",
        "Режим Мудреца",
        "Восемь Врат",
        "Эдо Тенсей",
        "Техника Теневого Клонирования",
        "Гендзюцу",
    ],
    "events": [
        "Экзамены на Чуунина",
        "Четвёртая Мировая Война Шиноби",
        "Нападение Девятихвостого Демона-Лиса",
        "Падение Клана Учиха",
        "Сокрушение Конохи",
        "Нападение Пейна",
        "Бесконечное Цукуёми",
        "Долина Завершения",
        "Миссия Возвращения Саске",
        "Собрание Пяти Каге",
    ],
}


def api_get(params: dict) -> dict:
    query = urllib.parse.urlencode({"format": "json", **params})
    req = urllib.request.Request(
        f"{API_URL}?{query}", headers={"User-Agent": USER_AGENT}
    )

    last_error: Exception | None = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as exc:  # pragma: no cover - robustness for flaky network
            last_error = exc
            time.sleep(1)

    assert last_error is not None
    raise last_error


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w]+", "_", slug, flags=re.UNICODE)
    return slug.strip("_")


def remove_nested_templates(text: str) -> str:
    result = []
    depth = 0
    i = 0
    while i < len(text):
        if text[i : i + 2] == "{{":
            depth += 1
            i += 2
            continue
        if text[i : i + 2] == "}}" and depth > 0:
            depth -= 1
            i += 2
            continue
        if depth == 0:
            result.append(text[i])
        i += 1
    return "".join(result)


def clean_wikitext(raw: str) -> str:
    text = raw

    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<ref[^>/]*/>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<ref[^>]*?>.*?</ref>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<section\s+[^>]+/>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    text = remove_nested_templates(text)
    text = re.sub(r"\{\|[\s\S]*?\|\}", "", text)

    text = re.sub(r"\[\[(?:File|Image):[^\]]+\]\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[\[(?:Category):[^\]]+\]\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[(https?://[^\s\]]+)\s+([^\]]+)\]", r"\2", text)
    text = re.sub(r"\[(https?://[^\]]+)\]", "", text)

    text = text.replace("'''", "")
    text = text.replace("''", "")
    text = text.replace("__TOC__", "")

    text = re.sub(r"<[^>]+>", "", text)

    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            cleaned_lines.append("")
            continue
        if re.search(r"\.(?:png|jpg|jpeg|gif|svg|webp)\|", line, flags=re.IGNORECASE):
            continue
        if re.match(r"^\d+px\|thumb\|", line, flags=re.IGNORECASE):
            continue
        if line.lower().startswith(("thumb|", "left|thumb|", "right|thumb|")):
            continue
        if line.startswith(("|", "!", ";", ":")):
            continue
        if line.startswith("__") and line.endswith("__"):
            continue

        line = re.sub(r"^=+\s*(.*?)\s*=+$", r"\1", line)
        line = re.sub(r"\s+", " ", line)
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def resolve_title(entity_name: str) -> str:
    page_resp = api_get({"action": "query", "titles": entity_name})
    pages = page_resp.get("query", {}).get("pages", {})
    for page in pages.values():
        if "missing" not in page:
            return page["title"]

    search_resp = api_get(
        {
            "action": "query",
            "list": "search",
            "srsearch": entity_name,
            "srlimit": 1,
        }
    )
    results = search_resp.get("query", {}).get("search", [])
    if not results:
        raise ValueError(f"No page found for: {entity_name}")
    return results[0]["title"]


def fetch_wikitext(page_title: str) -> tuple[str, str]:
    parsed = api_get(
        {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "redirects": 1,
        }
    )
    final_title = parsed["parse"]["title"]
    return final_title, parsed["parse"]["wikitext"]["*"]


def save_entity(category: str, query_name: str) -> tuple[str, str, int]:
    resolved_title = resolve_title(query_name)
    final_title, raw = fetch_wikitext(resolved_title)
    clean_text = clean_wikitext(raw)

    filename = f"{category}__{slugify(query_name)}.txt"
    out_path = OUT_DIR / filename

    header = [
        f"Entity: {final_title}",
        f"Category: {category}",
        # f"Source: https://naruto.fandom.com/ru/wiki/{final_title.replace(' ', '_')}",
        "",
    ]
    out_path.write_text("\n".join(header) + clean_text + "\n", encoding="utf-8")
    return query_name, final_title, len(clean_text)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report = []
    failures = []

    for category, names in ENTITIES.items():
        for name in names:
            try:
                report.append(save_entity(category, name))
                print(f"OK: {name}")
            except Exception as exc:  # pragma: no cover
                failures.append((name, str(exc)))
                print(f"FAIL: {name} -> {exc}")

    summary_lines = [
        "Narutopedia Knowledge Base Build Report",
        "",
        f"Total requested: {sum(len(v) for v in ENTITIES.values())}",
        f"Successfully saved: {len(report)}",
        f"Failed: {len(failures)}",
        "",
        "Saved entities:",
    ]
    summary_lines.extend(
        f"- {query_name} -> {resolved_title} ({char_count} chars)"
        for query_name, resolved_title, char_count in report
    )

    if failures:
        summary_lines.append("")
        summary_lines.append("Failures:")
        summary_lines.extend(f"- {name}: {error}" for name, error in failures)

    (OUT_DIR / "_build_report.txt").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )

    print("\nBuild complete.")
    print(f"Saved: {len(report)} | Failed: {len(failures)}")


if __name__ == "__main__":
    main()