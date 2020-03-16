import requests
import time
import hmac
import hashlib
import urllib
import datetime

import src.env as env


class Coincheck():
    def __init__(self):
        self.base_url = "https://coincheck.com"
        self.access_key = env.COINCHECK_API_KEY
        self.secret_key = env.COINCHECK_API_SECRET

    def _get_url(self, path):
        return "".join([self.base_url, path])

    def _get_signature(self, message):
        signature = hmac.new(self.secret_key.encode(), message.encode(),
                             hashlib.sha256).hexdigest()

        return signature

    def _get_headers(self, access_key, nonce, signature):
        headers = {
            'Content-Type': 'application/json',
            'ACCESS-KEY': access_key,
            'ACCESS-NONCE': nonce,
            'ACCESS-SIGNATURE': signature
        }

        return headers

    def _nonce(self):
        # このnonceの値をいじるとapi keyを新規発行しないといけいなので触らないこと。
        return str(int(time.time()))

    def _gdddet(self, path, params=None):
        if params:
            path = path + "?" + urllib.parse.urlencode(params)

        url = self.base_url + path
        nonce = self._nonce()
        signature = self._get_signature(url)
        headers = self._get_headers(self.access_key, nonce, signature)

        return requests.get(url, headers=headers).json()

    def _get(self, endpoint, params=None):
        self.nonce = str(int(time.time()))

        url = '%s/%s' % (self.base_url, endpoint)

        request_args = {}
        params = params or {}

        request_args['headers'] = params
        if type(params) is dict:
            url_endpoint = "?"
        for (key, value) in params.items():
            url_endpoint += str(key) + "=" + str(value) + "&"
        url += url_endpoint[:-1]

        message = bytes(self.nonce + url, 'ascii')
        signature = hmac.new(bytes(self.secret_key, 'ascii'),
                             msg=message,
                             digestmod=hashlib.sha256).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "ACCESS-KEY": self.access_key,
            "ACCESS-NONCE": self.nonce,
            "ACCESS-SIGNATURE": signature
        }
        request_args['headers'].update(headers)

        response = requests.get(url, **request_args)
        content = response.json()

        return content

    # https://coincheck.com/ja/documents/exchange/api#order-transactions
    def _create_fetch_trades_params(self, id=None):
        limit = 25  # 1回のpaginateの最大は25
        params = {
            "limit": str(limit),
            "order": "desc",  # 新しい順
        }

        if id:
            params["starting_after"] = str(id)

        return params

    def fetch_my_trades(self):
        end_point = "api/exchange/orders/transactions_pagination"

        index_id = None
        trades = []

        for _ in range(10):
            params = self._create_fetch_trades_params(index_id)
            res = self._get(end_point, params=params)
            time.sleep(1)

            if res["success"]:
                transactions = res["data"]
                index_id = int(transactions[-1]["id"])

                trades.extend(transactions)
            else:
                print(res["error"])
                break

        return trades
