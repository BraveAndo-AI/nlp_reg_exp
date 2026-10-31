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

python regex_extract.py eval annotate.csv           # 2: таблица precision/recall

python clean_text.py                                # 3: демо очистки

python sent_split.py sample corpus_ru.txt           # 4: sent_gold.txt

python sent_split.py eval sent_gold.txt --lang ru   # 4: таблица + типы ошибок
```



## Полезные ссылки
- Правила User-Agent для Wikimedia: https://meta.wikimedia.org/wiki/User-Agent_policy
- Wikipedia API (extracts): https://www.mediawiki.org/wiki/Extension:TextExtracts
- Датасет Википедии на HF: https://huggingface.co/datasets/wikimedia/wikipedia
- Регулярные выражения в Python: https://docs.python.org/3/library/re.html
- Тренажёр регулярок: https://regex101.com
- spaCy, модели для русского: https://spacy.io/models/ru
- NLTK, токенизация: https://www.nltk.org/api/nltk.tokenize.html
- Jurafsky & Martin, гл. 2 (regex, нормализация, предложения): https://web.stanford.edu/~jurafsky/slp3/2.pdf
