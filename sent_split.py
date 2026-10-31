"""Задание 4. Разбиение на предложения: regex vs nltk.sent_tokenize vs spaCy.

Шаги:
  1) python sent_split.py sample corpus_ru.txt   -> sent_gold.txt (≈200 предложений, по одному на строку)
  2) ВРУЧНУЮ проверь sent_gold.txt: каждая строка = ровно одно правильное предложение
  3) python sent_split.py eval sent_gold.txt --lang ru   -> таблица + sent_errors.csv

Сравнение — по границам предложений (позициям в тексте): precision / recall / F1.
Каждая ошибка автоматически получает тип: сокращение, инициалы, многоточие, числа, кавычки/скобки, другое.
"""
import argparse
import re

UPPER = "A-ZА-ЯЁӘҒҚҢӨҰҮҺІ"
# граница: после . ! ? … идут пробелы, а затем заглавная буква / цифра / кавычка / тире
SPLIT_RE = re.compile(rf"(?<=[.!?…])\s+(?=[«\"„(\[—–-]?\s?[{UPPER}0-9])")

# частые сокращения (рус. + каз.), после которых обычно НЕ конец предложения
ABBR = {"т", "е", "д", "п", "г", "гг", "им", "др", "ст", "см", "стр", "проф", "акад", "доц",
        "ул", "обл", "р", "руб", "тыс", "млн", "млрд", "н", "э", "в", "вв", "напр", "рис",
        "ж", "жж", "б", "бет", "қ", "мыс"}


def ends_with_abbr(s):
    m = re.search(r"(\w+)\.$", s)
    if not m:
        return False
    w = m.group(1)
    return w.lower() in ABBR or (len(w) == 1 and w.isupper())   # сокращение или инициал


def regex_split(text, fix_abbr=True):
    parts = [p.strip() for p in SPLIT_RE.split(text) if p.strip()]
    if not fix_abbr:
        return parts
    out = []
    for p in parts:
        if out and ends_with_abbr(out[-1]):
            out[-1] += " " + p          # склеиваем: «т.е. Это» не граница
        else:
            out.append(p)
    return out


def get_splitters(lang):
    import nltk
    import spacy

    nltk.download("punkt_tab", quiet=True)
    if lang == "ru":
        nlp = spacy.load("ru_core_news_md")                 # границы по синтаксическому парсеру
    else:
        nlp = spacy.load("xx_ent_wiki_sm")                  # парсера нет -> правила sentencizer
        nlp.add_pipe("sentencizer")
    return {
        "regex (наивный)": lambda t: regex_split(t, fix_abbr=False),
        "regex + сокращения": regex_split,
        # для казахского punkt-модели нет — берём русскую
        "nltk.sent_tokenize": lambda t: nltk.sent_tokenize(t, language="russian"),
        "spaCy": lambda t: [s.text for s in nlp(t).sents],
    }


# ---------- сравнение границ ----------
def boundaries(text, sents):
    ends, pos = set(), 0
    for s in sents:
        s = s.strip()
        i = text.find(s, pos)
        if i == -1:
            continue
        pos = i + len(s)
        ends.add(pos)
    ends.discard(len(text))   # конец текста не считаем
    return ends


def error_type(left):
    last = left.split()[-1] if left.split() else ""
    if re.search(rf"(^|\.)[{UPPER}]\.$", last):
        return "инициалы"
    if last.endswith("…") or last.endswith("..."):
        return "многоточие"
    if re.search(r"\d[.)]$", last):
        return "числа/нумерация"
    words = re.findall(r"\w+", last)
    if words and last.endswith(".") and words[-1].lower() in ABBR:
        return "сокращение"
    if re.search(r"[\"»)\]]$", last):
        return "кавычки/скобки"
    return "другое"


def evaluate(gold_path, lang):
    import pandas as pd

    gold_sents = [l.strip() for l in open(gold_path, encoding="utf-8") if l.strip()]
    text = " ".join(gold_sents)
    gold = boundaries(text, gold_sents)

    rows, errors = [], []
    for name, split in get_splitters(lang).items():
        pred = boundaries(text, split(text))
        tp, fp, fn = len(pred & gold), len(pred - gold), len(gold - pred)
        p, r = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
        rows.append({"Метод": name, "Предложений": len(pred) + 1,
                     "Precision": round(p, 3), "Recall": round(r, 3),
                     "F1": round(2 * p * r / max(p + r, 1e-9), 3)})
        for b, kind in [(b, "лишняя граница") for b in pred - gold] + \
                       [(b, "пропущена граница") for b in gold - pred]:
            errors.append({"method": name, "error": kind, "type": error_type(text[:b]),
                           "context": text[max(0, b - 50):b] + " ‖ " + text[b:b + 30]})

    print(f"Эталон: {len(gold_sents)} предложений\n")
    print(pd.DataFrame(rows).to_markdown(index=False))
    err = pd.DataFrame(errors)
    if len(err):
        print("\nТипы ошибок:")
        print(pd.crosstab(err["type"], err["method"]).to_markdown())
    err.to_csv("sent_errors.csv", index=False)


def sample(corpus_path, n=220):
    import nltk

    nltk.download("punkt_tab", quiet=True)
    sents = []
    for para in open(corpus_path, encoding="utf-8"):
        if para.strip():
            sents += nltk.sent_tokenize(para.strip(), language="russian")
        if len(sents) >= n:
            break
    open("sent_gold.txt", "w", encoding="utf-8").write("\n".join(sents[:n]))
    print("sent_gold.txt готов. ВНИМАТЕЛЬНО исправь границы вручную (склей/раздели строки).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample", "eval", "demo"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--lang", default="ru", choices=["ru", "kk"])
    a = ap.parse_args()
    if a.cmd == "sample":
        sample(a.path)
    elif a.cmd == "eval":
        evaluate(a.path, a.lang)
    else:
        t = "Лекцию читал проф. А.С. Пушкин. Он говорил, т.е. объяснял... Потом ушёл! В 1998 г. было иначе."
        print(regex_split(t, fix_abbr=False))
        print(regex_split(t))
