from services.exchange import ExchangeService


def test_normalize_conversational_usd_amounts():
    cases = [
        (15, "15 белый", "usd", 15000),
        (10, "10 бел", "usd", 10000),
        (15, "15 син", "usdnew", 15000),
        (10, "10$", "usd", 10000),
        (15, "15 долларов", "usd", 15000),
        (10, "10к", "", 10000),
        (10, "10 тыс", "", 10000),
    ]

    for amount, raw_text, currency, expected in cases:
        assert ExchangeService.normalize_amount(
            amount,
            raw_text,
            currency,
        ) == expected


def test_normalize_does_not_expand_full_or_non_usd_amounts():
    assert ExchangeService.normalize_amount(10000, "10000$", "usd") == 10000
    assert ExchangeService.normalize_amount(50, "50 долларов", "usd") == 50
    assert ExchangeService.normalize_amount(10, "10 евро", "eur") == 10
