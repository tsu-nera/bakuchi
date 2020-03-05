import ccxt  # noqa
from src.constants.ccxtconst import EXCHANGE_AUTH_DICT, API_KEY, API_SECRET


def fetch_balance(exchange_id):
    ex = eval('ccxt.{}()'.format(exchange_id))
    auth = EXCHANGE_AUTH_DICT[exchange_id]
    ex.apiKey = auth[API_KEY]
    ex.secret = auth[API_SECRET]

    print(ex.fetch_balance())
