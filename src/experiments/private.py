import ccxt
import src.env as env


def fetch_bitflyer_balance():
    bf = ccxt.bitflyer()
    bf.apiKey = env.BITFLYER_API_KEY
    bf.secret = env.BITFLYER_API_SECRET

    print(bf.fetch_balance())
