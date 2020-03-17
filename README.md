# bakuchi

仮想通貨 Bot トレード開発

## 概要

仮想通貨 Bot を開発して億り人になり、武蔵小杉のタワマンに住むためのプロジェクト。

戦略は、とりあえずローリスク・ローリターンのアービトラージ([裁定取引](https://ja.wikipedia.org/wiki/%E8%A3%81%E5%AE%9A%E5%8F%96%E5%BC%95))で実装する。

## Environments

- python 3.7
- ccxt 1.23

インフラまわりはとりあえず自宅のゲーミングサーバ(Ubuntu 18.04)で常時稼働。

## Getting Started

```
$ git clone https://github.com/tsu-nera/bakuchi.git
$ cd bakuchi

# 各取引所の認証情報を記載
$ cp src/.env.sample src/.env
$ emacs -nw src/.env

# pythonのライブラリいろいろいれる(TODO: あとで必須のものを追記)
$ pip install ccxt invoke python-dotenv
$ pip install tablulate urllib3
$ pip install numpy pandas jupyter notebook matplotlib

# Bot稼働
$ inv trade
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
$ inv trade

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

### その他

あとでちゃんと書く。

## 取引所

### Bot 稼働でつかっている取引所

- [Coincheck](https://coincheck.com/ja/)
- [Liquid](https://www.liquid.com/ja/)

### 口座開設済みの取引所

- [bitFlyer](https://bitflyer.com/ja-jp/)
- [bitbank](https://bitbank.cc/)
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

## References

5 年前の FX シストレ失敗作

- [oanda-forex-study](https://github.com/tsu-nera/oanda-forex-study)

## Author

[@tsu_crypt](https://twitter.com/tsu_crypt)
