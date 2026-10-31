"""5 положительных и 5 отрицательных примеров на каждый шаблон.  Запуск: pytest test_regex.py -v"""
import pytest

from regex_extract import extract

EXAMPLES = {
    "DATE": (
        ["12.05.2024", "2024-05-12", "5/3/24", "12 мая 2024", "3 мамырда"],
        ["версия 3.10.2", "32.13.2024", "в 2024 году", "12 мамонтов", "IP 192.168.0.1"],
    ),
    "EMAIL": (
        ["ivan.petrov@mail.ru", "a_b+tag@gmail.com", "info@kbtu.kz", "test-user@sub.domain.org", "x@y.co"],
        ["ivan@", "@mail.ru", "ivan@mail", "ivan mail.ru", "ivan@@mail.ru"],
    ),
    "URL": (
        ["https://kbtu.kz/ru/news", "http://example.com?a=1&b=2", "www.google.com", "kaspi.kz",
         "https://kk.wikipedia.org/wiki/Қазақстан"],
        ["ivan@mail.ru", "т.е.", "файл report.pdf", "http//broken", "число 3.14"],
    ),
    "PHONE": (
        ["+7 701 234 56 78", "87012345678", "8 (727) 250-12-34", "+7-777-123-45-67", "+77011234567"],
        ["+7 912 345 67 89", "8 701 234 56", "1234567890", "88005553535", "2024-05-12"],
    ),
    "MONEY": (
        ["5 000 тенге", "1500 тг", "2,5 млн теңге", "100₸", "15000 KZT"],
        ["5000 рублей", "$100", "просто тенге", "100 человек", "2 тыс. рублей"],
    ),
    "ABBR": (
        ["РК", "ҚР", "КБТУ", "NLP", "ООН"],
        ["Казахстан", "XIX век", "буква А", "ВНИМАНИЕПРОВЕРКА", "iPhone"],
    ),
}

POS = [(name, s) for name, (pos, _) in EXAMPLES.items() for s in pos]
NEG = [(name, s) for name, (_, neg) in EXAMPLES.items() for s in neg]


@pytest.mark.parametrize("name,text", POS)
def test_positive(name, text):
    # шаблон должен найти строку целиком
    assert extract(name, f"текст {text} текст") == [text]


@pytest.mark.parametrize("name,text", NEG)
def test_negative(name, text):
    assert extract(name, text) == []
