from os import getenv
from functions.db_main import Database
from re import compile, IGNORECASE
API_BASE = getenv("API")
API_KEY = getenv("API_KEY")
PARSER_EXCHANGER = getenv("PARSER_EXCHANGER")
# URL_GOLD = getenv("URL_GOLD")
TELEGRAM_TOKEN = getenv("TOKEN")

SECRETARY_TOKEN = getenv("TOKEN")
ADMIN_CHAT_ID = getenv("Admin")

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
PRIVATE_OBMEN = getenv("PRIVATE_OBMEN")
EXPRIVATUA = getenv("EXPRIVATUA")

HEADERS = {
    "Authorization": f"ApiKey {API_KEY}"
}
db = Database()

API_URL_CURRENCYS = f'{getenv("API")}/api/v1/currencys/?limit=115'
CURRENCYS_NOVYY_RYNOK = f'{getenv("API")}/api/v1/currencys/?exchanger=4&limit=23'


USD_PATTERN = compile(
    r'USD\s*:\s*(\d+(?:[.,]\d+)?)\s*/\s*(\d+(?:[.,]\d+)?)',
    IGNORECASE
)
PATTERN = compile(r'^([+-]?\d+)\s+([а-яА-Я]+)\*(\d+[.,]?\d*)$')
EUR_PATTERN = compile(r"(евро|eur|ев)")
B_PATTERN = compile(r"б\*\s*\d+[.,]\d+")


TRADE_PATTERN = compile(
    r'([+-])(\d+)(дол син|дол б|евро|eur)'
    r'(б|бел|син)?\*(\d+(?:\.\d+)?)'
)
BALANCE_USD_PATTERN = compile(
    r"(ск|сколько)[^\w]?(б|usd)[^\w]?(есть)?", IGNORECASE)
