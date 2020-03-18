import os
import shutil
import traceback

import src.constants.ccxtconst as ccxtconst
from src.libs.asset import Asset

from src.core.arbitrage_trading import ArbitrageTrading

from src.libs.logger import get_trading_logger_with_stdout

from src.libs.slack_client import SlackClient
import src.env as env
import src.constants.path as path

TRADES_LOGS = [
    path.CCXT_LOG_FILE_PATH, path.MARGIN_LOG_FILE_PATH,
    path.ASSET_LOG_FILE_PATH, path.TRADING_LOG_FILE_PATH
]


def backup_trading_logs(backup_dir_path):
    for file in TRADES_LOGS:
        if os.path.exists(file):
            shutil.copy(file, backup_dir_path)


def clean_trading_logs():
    for file in TRADES_LOGS:
        if os.path.exists(file):
            # os.removeだと loggerとの関係がうまくいかなかった
            with open(file, 'w'):
                pass


def run_trading(demo_mode=False):
    clean_trading_logs()
    logger = get_trading_logger_with_stdout()
    asset = Asset()
    slack = SlackClient(env.SLACK_WEBHOOK_URL_TRADE)

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
        logger.info("keyboard interuption occured. stop trading bot...")
    except Exception as e:
        # エラー発生したらログとslack通知
        slack_error = SlackClient(env.SLACK_WEBHOOK_URL_ERROR)
        slack_error.notify_error(traceback.format_exc())
        logger.exception(e)
    finally:
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
