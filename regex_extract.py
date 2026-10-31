"""Задание 2. Регулярные выражения: даты, e-mail, URL, телефоны РК, суммы в тенге, аббревиатуры.

Шаги:
  1) pytest test_regex.py                        — 5 положительных и 5 отрицательных примеров на шаблон
  2) python regex_extract.py sample corpus.txt   — 100 строк в annotate.csv (уже с ответами регулярок)
  3) вручную исправить annotate.csv (это и есть эталон!)
  4) python regex_extract.py eval annotate.csv   — таблица precision / recall
"""
import random
import re
import sys
from collections import Counter

RU_MONTHS = r"январ|феврал|март|апрел|ма[йяе]|июн|июл|август|сентябр|октябр|ноябр|декабр"
KK_MONTHS = r"қаңтар|ақпан|наурыз|сәуір|мамыр|маусым|шілде|тамыз|қыркүйек|қазан|қараша|желтоқсан"
DAY = r"(?:0?[1-9]|[12]\d|3[01])"
MONTH = r"(?:0?[1-9]|1[0-2])"
UPPER = "A-ZА-ЯЁӘҒҚҢӨҰҮҺІ"
URL_END = r"[^\s<>\"«».,;:!?)\]]"   # URL не должен заканчиваться точкой/запятой

PATTERNS = {
    # 12.05.2024 | 12/05/24 | 2024-05-12 | 12 мая 2024 | 12 мамырда (каз. окончания: \w*)
    "DATE": re.compile(
        rf"\b(?:\d{{4}}-{MONTH}-{DAY}"
        rf"|{DAY}[./-]{MONTH}[./-](?:\d{{4}}|\d{{2}})"
        rf"|{DAY}\s+(?:{RU_MONTHS}|{KK_MONTHS})\w*(?:\s+\d{{4}})?)\b",
        re.IGNORECASE),

    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b"),

    # с протоколом / www. — или голый домен .kz/.ru/... (но не часть e-mail)
    "URL": re.compile(
        rf"(?:https?://|www\.)[^\s<>\"«»]*{URL_END}"
        rf"|(?<![@\w.-])[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:kz|ru|com|org|net|io)\b(?:/[^\s<>\"«»]*{URL_END})?",
        re.IGNORECASE),

    # +7 7XX XXX XX XX, 8 (7XX) XXX-XX-XX, 87XXXXXXXXX — код после +7/8 начинается с 7 (Казахстан)
    "PHONE": re.compile(r"(?<![\d+])(?:\+7|8)[\s-]?\(?7\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}(?!\d)"),

    # 5 000 тенге | 2,5 млн теңге | 1500 тг | 100₸ | 15000 KZT
    "MONEY": re.compile(
        r"(?<![\d,.])(?:\d{1,3}(?:[   ]\d{3})+|\d+)(?:[.,]\d+)?\s?"
        r"(?:(?:тыс|млн|млрд|трлн|мың)\.?\s?)?"
        r"(?:(?:тенге|теңге)\w*|тг\.?(?!\w)|₸|KZT(?!\w))",
        re.IGNORECASE),

    # 2–6 заглавных букв подряд (РК, ҚР, КБТУ, NLP), кроме римских цифр (XIX)
    "ABBR": re.compile(rf"\b(?![IVXLCDM]+\b)[{UPPER}]{{2,6}}\b"),
}


def extract(name, text):
    return [m.group(0).strip() for m in PATTERNS[name].finditer(text)]


def extract_all(text):
    return {name: extract(name, text) for name in PATTERNS}


# ---------- 100 строк для ручной разметки ----------
def sample(corpus_path, n=100, seed=42):
    import pandas as pd

    lines = [l.strip() for l in open(corpus_path, encoding="utf-8") if 30 < len(l.strip()) < 600]
    rnd = random.Random(seed)
    with_hits = [l for l in lines if any(extract_all(l).values())]
    k = min(len(with_hits), int(n * 0.7))   # 70% строк, где что-то нашлось, 30% — случайные
    chosen = rnd.sample(with_hits, k) + rnd.sample(lines, n - k)
    rows = [{"text": t, **{k: " | ".join(v) for k, v in extract_all(t).items()}} for t in chosen]
    pd.DataFrame(rows).to_csv("annotate.csv", index=False)
    print("annotate.csv готов. Исправь колонки вручную: убери ложные, допиши пропущенные (через ' | ').")


# ---------- precision / recall ----------
def evaluate(gold_path):
    import pandas as pd

    df = pd.read_csv(gold_path).fillna("")
    rows = []
    for name in PATTERNS:
        tp = fp = fn = 0
        for text, cell in zip(df["text"], df[name]):
            gold = Counter(v.strip() for v in str(cell).split("|") if v.strip())
            pred = Counter(extract(name, text))
            hit = sum((gold & pred).values())
            tp, fp, fn = tp + hit, fp + sum(pred.values()) - hit, fn + sum(gold.values()) - hit
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        rows.append({"Шаблон": name, "TP": tp, "FP": fp, "FN": fn,
                     "Precision": round(p, 3), "Recall": round(r, 3), "F1": round(f1, 3)})
    res = pd.DataFrame(rows)
    print(res.to_markdown(index=False))
    res.to_csv("regex_table.csv", index=False)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sample":
        sample(sys.argv[2])
    elif cmd == "eval":
        evaluate(sys.argv[2])
    else:
        demo = ("Встреча 12 мая 2024 года в КБТУ, пишите на info@kbtu.kz или https://kbtu.kz/ru. "
                "Тел.: +7 701 234 56 78, взнос 5 000 тенге. Жиналыс 3 мамырда өтеді, ҚР заңы.")
        for k, v in extract_all(demo).items():
            print(f"{k:6} {v}")
