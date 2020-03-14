import src.utils.private as private
import src.constants.ccxtconst as ccxtconst
from src.libs.asset import Asset

from src.config import config

from src.core.arbitrage_trading import ArbitrageTrading

from src.libs.logger import get_trading_logger_with_stdout


def run_trading():
    logger = get_trading_logger_with_stdout()
    asset = Asset()

    demo_mode = int(config["trade"]["demo_mode"])

    if demo_mode == 1:
        logger.info("==================================== ")
        logger.info("=== trading bot start(dmeo mode) === ")
        logger.info("==================================== ")
    else:
        logger.info("========================= ")
        logger.info("=== trading bot start === ")
        logger.info("========================= ")

    asset.logging()

    # run trade
    arbitrage = ArbitrageTrading(ccxtconst.EXCHANGE_ID_LIQUID,
                                 ccxtconst.EXCHANGE_ID_COINCHECK,
                                 ccxtconst.SYMBOL_BTC_JPY)

    try:
        arbitrage.run()
    except KeyboardInterrupt:
        # Botを手動で止めるときはCtrl+Cなのでそのアクションを捕捉
        asset.logging()

        print()
        print()
        logger.info("======================= ")
        logger.info("=== trading bot end === ")
        logger.info("======================= ")
