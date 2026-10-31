"""Скачать ≥ 50 000 слов из Википедии (ru или kk) в corpus_<lang>.txt.

Почему Википедия «блокирует» и как это обойти правильно:
  * 403 Forbidden — запросы без User-Agent (или с UA по умолчанию python-requests).
    Правила Wikimedia требуют понятный User-Agent с контактом -> ставим его.
  * 429 Too Many Requests — слишком частые запросы -> пауза + повтор.
  * Не парсим HTML-страницы, а берём текст через официальный API (сразу чистый текст).
  * Самый быстрый путь вообще без запросов к сайту — готовый дамп на Hugging Face (по умолчанию).

Запуск:
  python get_data.py --lang kk                 # быстро, через Hugging Face (~1 мин)
  python get_data.py --lang ru --source api    # через API Википедии
"""
import argparse
import time

MIN_WORDS = 150  # короткие статьи-заготовки пропускаем


def from_hf(lang):
    from datasets import load_dataset

    # streaming=True — не качаем весь дамп, читаем статьи по одной
    ds = load_dataset("wikimedia/wikipedia", f"20231101.{lang}", split="train", streaming=True)
    for art in ds:
        yield art["title"], art["text"]


def from_api(lang, email):
    import requests

    s = requests.Session()
    s.headers["User-Agent"] = f"NLP-course-student/1.0 (educational project; {email})"
    api = f"https://{lang}.wikipedia.org/w/api.php"

    def get(params):
        params = {**params, "format": "json", "formatversion": 2, "maxlag": 5}
        for _ in range(5):
            r = s.get(api, params=params, timeout=30)
            data = r.json() if r.status_code == 200 else {}
            if r.status_code == 200 and "error" not in data:
                return data
            time.sleep(int(r.headers.get("Retry-After", 5)))  # 429 / maxlag -> ждём
        raise RuntimeError(f"API не отвечает: {r.status_code}")

    while True:
        rnd = get({"action": "query", "list": "random", "rnnamespace": 0, "rnlimit": 50})
        for page in rnd["query"]["random"]:
            data = get({"action": "query", "prop": "extracts", "explaintext": 1,
                        "titles": page["title"]})
            yield page["title"], data["query"]["pages"][0].get("extract", "")
            time.sleep(0.1)  # вежливая пауза


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="kk", choices=["kk", "ru"])
    ap.add_argument("--words", type=int, default=60_000)
    ap.add_argument("--source", default="hf", choices=["hf", "api"])
    ap.add_argument("--email", default="your_email@example.com", help="контакт для User-Agent")
    args = ap.parse_args()

    gen = from_hf(args.lang) if args.source == "hf" else from_api(args.lang, args.email)
    out = f"corpus_{args.lang}.txt"
    total, n, seen = 0, 0, set()
    with open(out, "w", encoding="utf-8") as f:
        for title, text in gen:
            words = len(text.split())
            if title in seen or words < MIN_WORDS:
                continue
            seen.add(title)
            f.write(text.strip() + "\n\n")
            total, n = total + words, n + 1
            if total >= args.words:
                break
    print(f"{out}: {n} статей, {total} слов")
