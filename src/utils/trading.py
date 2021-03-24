import os
import ccxt
import shutil
import traceback

import src.constants.ccxtconst as ccxtconst
from src.libs.asset import Asset
from src.libs.profit import Profit

from src.core.arbitrage_trading import ArbitrageTrading

from src.loggers.logger import get_trading_logger_with_stdout

from src.libs.slack_client import SlackClient
import src.env as env
import src.constants.path as path


def backup_trading_logs(current_trading_dir):
    target_dir_path = os.path.join(current_trading_dir, path.LOG_DIR)
    os.mkdir(target_dir_path)

    for file in path.TRADES_LOGS:
        if os.path.exists(file):
            file_name = os.path.basename(file)
            target_file_path = os.path.join(target_dir_path, file_name)
            shutil.copy(file, target_file_path)


def backup_trading_assets(current_trading_dir):
    target_dir_path = os.path.join(current_trading_dir, path.ASSETS_DIR)
    os.mkdir(target_dir_path)

    for file in path.TRADES_ASSETS:
        if os.path.exists(file):
            file_name = os.path.basename(file)
            target_file_path = os.path.join(target_dir_path, file_name)
            shutil.copy(file, target_file_path)


def backup_trading_orders(current_trading_dir):
    target_dir_path = os.path.join(current_trading_dir, path.ORDERS_DIR)
    os.mkdir(target_dir_path)

    file = path.ORDER_CSV_FILE_PATH
    if os.path.exists(file):
        file_name = os.path.basename(file)
        target_file_path = os.path.join(target_dir_path, file_name)
        shutil.copy(file, target_file_path)

    file = path.PROFIT_CSV_FILE_PATH
    if os.path.exists(file):
        file_name = os.path.basename(file)
        target_file_path = os.path.join(target_dir_path, file_name)
        shutil.copy(file, target_file_path)

    for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
        file = "{}.csv".format(exchange_id)
        if os.path.exists(file):
            file_name = os.path.basename(file)
            target_file_path = os.path.join(target_dir_path, file_name)
            shutil.copy(file, target_file_path)


def clean_trading_logs():
    for file in path.TRADES_LOGS:
        if os.path.exists(file):
            # os.removeだと loggerとの関係がうまくいかなかった
            with open(file, 'w'):
                pass


def clean_trading_assets():
    for file in path.TRADES_ASSETS:
        if os.path.exists(file):
            # os.removeだと loggerとの関係がうまくいかなかった
            with open(file, 'w'):
                pass


def run_trading(demo_mode=False):
    clean_trading_logs()
    clean_trading_assets()

    logger = get_trading_logger_with_stdout()
    asset = Asset()
    profit = Profit()
    profit.setDaemon(True)
    slack = SlackClient(env.SLACK_WEBHOOK_URL_TRADE)

    # run trade
    arbitrage = ArbitrageTrading(ccxtconst.ExchangeId.LIQUID,
                                 ccxtconst.ExchangeId.BITBANK,
                                 ccxtconst.SYMBOL_BTC_JPY,
                                 demo_mode=demo_mode)

    current_trading_dir = arbitrage.get_current_trading_data_dir()

    if demo_mode:
        logger.info("====================================")
        logger.info("=== trading bot start(demo mode) ===")
        logger.info("====================================")
    else:
        logger.info("=========================")
        logger.info("=== trading bot start ===")
        logger.info("=========================")
        slack.notify_with_datetime("Trading Botの稼働を開始しました。")
        asset.save(asset.TRADIGNG_START)
        profit.start()

    try:
        arbitrage.run()
    except KeyboardInterrupt:
        # Botを手動で止めるときはCtrl+Cなのでそのアクションを捕捉
        logger.info("keyboard interuption occured. stop trading bot...")
    except ccxt.InsufficientFunds:
        # circuit breaker でログを残しているのでここでログしなくてもいい。
        slack_error = SlackClient(env.SLACK_WEBHOOK_URL_ERROR)
        slack_error.notify_error(traceback.format_exc())
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
            asset.save(asset.TRADING_END)
            backup_trading_logs(current_trading_dir)
            backup_trading_assets(current_trading_dir)
            backup_trading_orders(current_trading_dir)
            slack.notify_with_datetime("Trading Botの稼働を終了しました。")
