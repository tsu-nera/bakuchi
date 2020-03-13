import src.constants.ccxtconst as cctxconst

from src.core.arbitrage_trading import ArbitrageTrading

from src.libs.logger import get_trading_logger


def run_trading():
    message = "== trading bot start == "

    logger = get_trading_logger()

    print(message)
    logger.info('%s', message)

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
