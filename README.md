bakuchi
===

仮想通貨Botトレード開発

## 概要

仮想通貨Botを開発して億り人になり、武蔵小杉のタワマンに住むためのプロジェクト。

戦略は、とりあえずローリスク・ローリターンのアービトラージ(裁定取引)で実装する。

* [裁定取引 \- Wikipedia](https://ja.wikipedia.org/wiki/%E8%A3%81%E5%AE%9A%E5%8F%96%E5%BC%95)

いまいちうまくいかなければ他の戦略を考えることにする。

## Getting Started

`src/.env.sample`をコピーして`src/.env`を作成。認証情報を記載する。


### トレード

終了はCtrl+c。デモトレードは `src/config.ini`で指定できる。

```
$ inv trade
```

### バックテスト

バックテストのためには、事前にデータを用意する。

```
$ inv backtest [data/historicals配下のディレクトリ名]
```

## 対応した取引所

* [Coincheck](https://coincheck.com/ja/)
* [Liquid](https://www.liquid.com/ja/)

### 対応予定の取引所

* [bitFlyer](https://bitflyer.com/ja-jp/)
* [bitbank](https://bitbank.cc/)
* [BitMEX](https://www.bitmex.com/)

## 開発リファレンス

* [cctx](https://github.com/ccxt/ccxt)
* [cctx doc](https://github.com/ccxt/ccxt/wiki)

## Links

5年前のFXシストレ失敗作はこちら。

* https://github.com/tsu-nera/oanda-forex-study/

## Author

[@tsu_crypt](https://twitter.com/tsu_crypt)
