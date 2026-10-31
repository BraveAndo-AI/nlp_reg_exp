"""Задание 3. Очистка текста.

clean_text(text):
  1) чинит «кракозябры» (UTF-8, прочитанный как cp1251: «РџСЂРёРІРµС‚» -> «Привет»)
  2) удаляет HTML (<script>/<style> целиком, остальные теги) и HTML-сущности (&nbsp; &quot;)
  3) Unicode NFC, удаляет невидимые символы (zero-width, мягкий перенос, BOM)
  4) нормализует кавычки и тире
  5) исправляет смешение латиницы и кириллицы в одном слове (Пpивeт -> Привет)
  6) нормализует пробелы и пустые строки
read_text(path) — читает файл в любой из частых кодировок и возвращает str (UTF-8 при записи).
"""
import html
import re
import unicodedata

# ---------- кодировка ----------
def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1251", "koi8-r"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


MOJIBAKE_RE = re.compile(r"[РС][Ѐ-џ]")   # типичные пары «Рџ», «СЂ»


def fix_mojibake(text):
    if len(MOJIBAKE_RE.findall(text)) < len(text) * 0.1:   # кракозябр мало — не трогаем
        return text
    try:
        return text.encode("cp1251").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


# ---------- смешение латиницы и кириллицы ----------
LAT = "aceopxyihABCEHKMOPTXI"
CYR = "асеорхуіһАВСЕНКМОРТХІ"     # визуально одинаковые буквы (і, һ — казахские)
LAT2CYR = str.maketrans(LAT, CYR)
CYR2LAT = str.maketrans(CYR, LAT)


def fix_mixed_word(word):
    n_lat = len(re.findall(r"[A-Za-z]", word))
    n_cyr = len(re.findall(r"[Ѐ-ӿ]", word))
    if n_lat == 0 or n_cyr == 0:
        return word
    # в какую сторону переводить — решает большинство букв
    return word.translate(LAT2CYR) if n_cyr >= n_lat else word.translate(CYR2LAT)


def fix_mixed_script(text):
    return re.sub(r"\w+", lambda m: fix_mixed_word(m.group(0)), text)


# ---------- основная функция ----------
def clean_text(text):
    text = fix_mojibake(text)

    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</p>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)

    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[​‌‍⁠﻿­]", "", text)

    text = re.sub(r"[«»“”„‟″]", '"', text)
    text = re.sub(r"[‘’‚‛′`]", "'", text)
    text = re.sub(r"[‐‑‒–—―]", "-", text)

    text = fix_mixed_script(text)

    text = re.sub(r"[ \t   ]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


if __name__ == "__main__":
    dirty = ('<div><p>Пpивeт,&nbsp;  мир!</p><script>alert(1)</script>'
             '<p>«Қазақстан» — “ел”​, iPhone и Тeлeфон</p></div>')
    print(repr(dirty))
    print(repr(clean_text(dirty)))
    print(repr(clean_text("РџСЂРёРІРµС‚, РјРёСЂ")))
