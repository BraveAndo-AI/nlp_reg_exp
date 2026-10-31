# ПР 1. Настройка среды и базовая обработка текста

| Файл | Задание |
|---|---|
| `requirements.txt`, `check_env.py` | 1 — окружение, версии, GPU |
| `get_data.py` | данные — ≥ 50 000 слов из Википедии |
| `regex_extract.py`, `test_regex.py` | 2 — регулярные выражения, precision/recall |
| `clean_text.py` | 3 — очистка текста |
| `sent_split.py` | 4 — разбиение на предложения, типы ошибок |
| `bibliography.md` | 5 статей ACL/NAACL 2023–2025 |
| `project.md` | одностраничное описание проекта |

## Порядок запуска

```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
# GPU (NVIDIA): pip install torch --index-url https://download.pytorch.org/whl/cu121
pip freeze > requirements.txt                       # фиксируем точные версии
python check_env.py                                 # 1

python get_data.py --lang kk                        # корпус ~1 минута
python get_data.py --lang ru

pytest test_regex.py -v                             # 2: 5+/5- примеров на шаблон (60 тестов)
python regex_extract.py sample corpus_ru.txt        # 2: annotate.csv (100 строк)
#   -> вручную исправить annotate.csv
python regex_extract.py eval annotate.csv           # 2: таблица precision/recall

python clean_text.py                                # 3: демо очистки

python sent_split.py sample corpus_ru.txt           # 4: sent_gold.txt
#   -> вручную исправить границы предложений
python sent_split.py eval sent_gold.txt --lang ru   # 4: таблица + типы ошибок
```

## Википедия и блокировки

- **Hugging Face (по умолчанию)** — самый быстрый вариант: готовый дамп `wikimedia/wikipedia`, сайт Википедии вообще не трогаем, лимитов нет.
- **API (`--source api`)** — если HF недоступен. Википедия отдаёт **403**, когда нет нормального User-Agent, и **429**, когда запросов слишком много. В скрипте стоит User-Agent с контактом (`--email`), пауза между запросами и повтор после 429. Текст берётся через API сразу без HTML.
- В Википедии мало e-mail, телефонов и сумм в тенге. Для задания 2 добавь в `annotate.csv` 20–30 строк из новостей или объявлений, иначе recall для этих шаблонов не на чем считать.

## Что писать в отчёт

- **Задание 2:** таблица `regex_table.csv`. Плюс 2–3 типичные ошибки: например, `ABBR` ловит слова капслоком («СТОП») и пропускает «ID» (похоже на римскую цифру), `URL` пропускает домены вне списка `.kz/.ru/.com/...`.
- **Задание 3:** пример до и после (`python clean_text.py`). Смешение алфавитов: в слове смотрим, каких букв больше, и заменяем «двойники» (`а/a`, `с/c`, `і/i`, `һ/h`...). Слова целиком на латинице (iPhone) не трогаются.
- **Задание 4:** таблица + crosstab «тип ошибки × метод» из `sent_split.py eval`. Ожидаемо: наивный regex режет на сокращениях и инициалах, nltk ошибается реже, spaCy (ru) опирается на синтаксис.

## Полезные ссылки
- Правила User-Agent для Wikimedia: https://meta.wikimedia.org/wiki/User-Agent_policy
- Wikipedia API (extracts): https://www.mediawiki.org/wiki/Extension:TextExtracts
- Датасет Википедии на HF: https://huggingface.co/datasets/wikimedia/wikipedia
- Регулярные выражения в Python: https://docs.python.org/3/library/re.html
- Тренажёр регулярок: https://regex101.com
- spaCy, модели для русского: https://spacy.io/models/ru
- NLTK, токенизация: https://www.nltk.org/api/nltk.tokenize.html
- Jurafsky & Martin, гл. 2 (regex, нормализация, предложения): https://web.stanford.edu/~jurafsky/slp3/2.pdf
