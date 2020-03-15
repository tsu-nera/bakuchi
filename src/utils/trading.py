import time
import src.utils.private as private
import src.constants.ccxtconst as ccxtconst
from src.libs.asset import Asset

from src.core.arbitrage_trading import ArbitrageTrading

from src.libs.logger import get_trading_logger_with_stdout, backup_trading_logs

from src.libs.slack_client import SlackClient


def run_trading(demo_mode=False):
    logger = get_trading_logger_with_stdout()
    asset = Asset()
    slack = SlackClient()

    if demo_mode:
        logger.info("====================================")
        logger.info("=== trading bot start(demo mode) ===")
        logger.info("====================================")
    else:
        logger.info("=========================")
        logger.info("=== trading bot start ===")
        logger.info("=========================")
        slack.notify_with_datetime("Trading Botの稼働を開始しました。")
        asset.logging()

    # run trade
    arbitrage = ArbitrageTrading(ccxtconst.EXCHANGE_ID_LIQUID,
                                 ccxtconst.EXCHANGE_ID_COINCHECK,
                                 ccxtconst.SYMBOL_BTC_JPY,
                                 demo_mode=demo_mode)

    try:
        arbitrage.run()
    except KeyboardInterrupt:
        # Botを手動で止めるときはCtrl+Cなのでそのアクションを捕捉
        asset.logging()

        print()
        print()
        if demo_mode:
            logger.info("==================================")
            logger.info("=== trading bot end(demo mode) ===")
            logger.info("==================================")
        else:
            logger.info("=======================")
            logger.info("=== trading bot end ===")
            logger.info("=======================")

            asset.logging()
            backup_trading_logs(arbitrage.get_current_trading_data_dir())
            slack.notify_with_datetime("Trading Botの稼働を終了しました。")
