"""Задание 1. Проверка окружения: версии библиотек, GPU, модели spaCy, NLTK, Transformers."""
import importlib

for pkg in ["nltk", "spacy", "transformers", "torch", "datasets", "pandas"]:
    try:
        print(f"{pkg:13} {importlib.import_module(pkg).__version__}")
    except ImportError:
        print(f"{pkg:13} НЕ УСТАНОВЛЕН")

# --- GPU ---
import torch

if torch.cuda.is_available():
    print("GPU: CUDA,", torch.cuda.get_device_name(0))
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    print("GPU: Apple MPS")
else:
    print("GPU: нет, работаем на CPU")

# --- spaCy ---
import spacy

for name in ["ru_core_news_md", "xx_ent_wiki_sm"]:
    nlp = spacy.load(name)
    doc = nlp("КБТУ находится в Алматы, а Назарбаев Университет — в Астане.")
    print(f"{name}: {[(e.text, e.label_) for e in doc.ents]}")

# --- NLTK ---
import nltk

nltk.download("punkt_tab", quiet=True)
print("NLTK:", nltk.sent_tokenize("Привет. Как дела?", language="russian"))

# --- Transformers (качается только токенизатор, ~1 МБ) ---
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
print("Transformers:", tok.tokenize("Қазақстан Республикасы"))
