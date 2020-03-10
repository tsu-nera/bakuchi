import src.constants.ccxtconst as cctxconst
from src.core.arbitrage_trading import ArbitrageTrading


def run_trading():
    print("== trading bot start == ")

    # run trade
    arbitrage = ArbitrageTrading(cctxconst.EXCHANGE_ID_LIQUID,
                                 cctxconst.EXCHANGE_ID_COINCHECK)

    try:
        arbitrage.run()
    except KeyboardInterrupt:
        # Botを手動で止めるときはCtrl+Cなのでそのアクションを捕捉
        print()
        print()
        print("== trading bot end == ")
