import src.constants.ccxtconst as cctxconst

from src.core.arbitrage_trading import ArbitrageTrading

import logging
import src.constants.common as common


def _get_logger():
    LOGGER_NAME = "trading"

    formatter = logging.Formatter('[%(levelname)s]%(asctime)s %(message)s')
    logfile = logging.FileHandler(common.TRADING_LOG_FILE_PATH, "w")
    logfile.setFormatter(formatter)
    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(logfile)

    return logger


def run_trading():
    message = "== trading bot start == "

    logger = _get_logger()

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
