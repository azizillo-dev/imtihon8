import json
from decimal import Decimal
from urllib.request import urlopen
from django.core.cache import cache


CBU_URL = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/"
RATES_CACHE_KEY = "cbu-rates"
RATES_TTL = 60 * 60


def get_rates():
    """1 birlik valyutaning so'mdagi narxi: {"UZS": 1, "USD": 12023.46, "EUR": 13461.47}"""
    rates = cache.get(RATES_CACHE_KEY)
    if rates:
        return rates

    with urlopen(CBU_URL, timeout=5) as response:
        data = json.load(response)

    rates = {"UZS": Decimal("1")}
    for item in data:
        if item["Ccy"] in ("USD", "EUR"):
            rates[item["Ccy"]] = Decimal(item["Rate"]) / Decimal(item["Nominal"])

    cache.set(RATES_CACHE_KEY, rates, timeout=RATES_TTL)
    return rates


def convert(amount, from_currency, to_currency, rates):
    # avval so'mga, keyin kerakli valyutaga o'tkaziladi
    return amount * rates[from_currency] / rates[to_currency]
