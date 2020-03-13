import src.constants.ccxtconst as cctxconst

from src.core.arbitrage_trading import ArbitrageTrading

from src.libs.logger import get_trading_logger_with_stdout


def run_trading():
    logger = get_trading_logger_with_stdout()

    logger.info("========================= ")
    logger.info("=== trading bot start === ")
    logger.info("========================= ")

    # run trade
    arbitrage = ArbitrageTrading(cctxconst.EXCHANGE_ID_LIQUID,
                                 cctxconst.EXCHANGE_ID_COINCHECK,
                                 cctxconst.SYMBOL_BTC_JPY)

    try:
        arbitrage.run()
    except KeyboardInterrupt:
        # Botを手動で止めるときはCtrl+Cなのでそのアクションを捕捉
        print()
        print()
        logger.info("======================= ")
        logger.info("=== trading bot end === ")
        logger.info("======================= ")
