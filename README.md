# bakuchi

仮想通貨 Bot トレード開発

## 概要

仮想通貨 Bot を開発して利益を出すためのプロジェクト。

ログや分析レポートは別リポジトリで管理。

* https://github.com/tsu-nera/bakuchi_analysis

戦略は、とりあえずローリスク・ローリターンのアービトラージ([裁定取引](https://ja.wikipedia.org/wiki/%E8%A3%81%E5%AE%9A%E5%8F%96%E5%BC%95))で実装する。

## Environments

- python 3.7
- ccxt 1.23

## Getting Started

```
$ git clone https://github.com/tsu-nera/bakuchi.git
$ cd bakuchi
$ git clone https://github.com/tsu-nera/bakuchi_analysis data

# 各取引所の認証情報を記載
$ cp src/.env.sample src/.env
$ emacs -nw src/.env

# pythonのライブラリいろいろいれる(TODO: あとで必須のものを追記)
$ conda install numpy pandas jupyter notebook matplotlib
$ pip install ccxt invoke python-dotenv
$ pip install tablulate urllib3 
$ conda install psutil sortedcontainers
$ pip install python-socketio[client]==4.6.1 # 5はダメっぽい

$ # pip install liquidtap --use-deprecated=legacy-resolver
  # なんか0.56.0じゃないと動かないぞ？なんだこりゃ
$ # https://reon777.com/2019/04/28/liquidtap/
$ # pip install websocket-client==0.56.0

$ pip install yapf flake8

# Bot稼働
$ inv bot
```

## ツール

タスクランナーには`invoke`を利用している。

```
$ pip install invoke
```

### トレード

終了は Ctrl+c。

```
# bot稼働
$ inv bot

# デモトレード: 実際のorderは実施しない。
$ inv demo-trade
```

### バックテスト

バックテストのためには、事前にデータを用意する。

```
# バックテスト
$ inv backtest [data/historicals配下のディレクトリ名]

# シミュレーション: バックテストを走らせている時に1secずつdelayをいれているだけ
$ inv simulate [data/historicals配下のディレクトリ名]
```

### cron設定

```
$ crontab -e

# 1時間ごとに実行
0 */1 * * *　~/repo/bakuchi/bin/asset-bot.sh
```

### その他

あとでちゃんと書く。

## 取引所

### Bot 稼働でつかっている取引所

- [Coincheck](https://coincheck.com/ja/)
- [Liquid](https://www.liquid.com/ja/)
- [bitbank](https://bitbank.cc/)

### 口座開設済みの取引所

- [bitFlyer](https://bitflyer.com/ja-jp/)
- [BitMEX](https://www.bitmex.com/)

### 口座開設はしないが検討はしている取引所

- Zaif
- BITPoint
- Huobi
- BTCBOX
- GMO コイン

## 開発リファレンス

- [cctx](https://github.com/ccxt/ccxt)
- [cctx doc](https://github.com/ccxt/ccxt/wiki)
- [coincheck api](https://coincheck.com/ja/documents/exchange/api)
- [liquid api](https://developers.liquid.com)
- [bitbank api](https://github.com/bitbankinc/bitbank-api-docs)

## References

5 年前の FX シストレ失敗作

- [oanda-forex-study](https://github.com/tsu-nera/oanda-forex-study)

## Author

[@tsu_crypt](https://twitter.com/tsu_crypt)
