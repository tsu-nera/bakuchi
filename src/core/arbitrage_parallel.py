import queue
import threading

from src.core.exchange_trading import ExchangeTrading as Exchange


class ArbitrageParallel():
    def __init__(self, exchange_id_x, exchange_id_y, symbol, demo_mode=False):
        self.ex_id_x = exchange_id_x
        self.ex_id_y = exchange_id_y
        self.exchage_ids = [self.ex_id_x, self.ex_id_y]

        self.symbol = symbol
        self.demo_mode = demo_mode

        self.exchange_x = Exchange(exchange_id_x, symbol, demo_mode=demo_mode)
        self.exchange_y = Exchange(exchange_id_y, symbol, demo_mode=demo_mode)

    def _request(self, func_x, func_y):
        responses = [None, None]

        def thread_worker(thread_queue):
            thread = thread_queue.get()
            try:
                if thread == 0:
                    responses[thread] = func_x()
                if thread == 1:
                    responses[thread] = func_y()
            except Exception as e:
                responses[thread] = e

            thread_queue.task_done()

        thread_queue = queue.Queue()

        for q in [0, 1]:
            thread_queue.put(q)

        while not thread_queue.empty():
            w_thread = threading.Thread(target=thread_worker,
                                        args=(thread_queue, ))
            w_thread.start()

        thread_queue.join()

        return responses[0], responses[1]

    def fetch_tick(self):
        func_x = lambda: self.exchange_x.fetch_tick()
        func_y = lambda: self.exchange_y.fetch_tick()

        return self._request(func_x, func_y)

    def order_buyx_selly(self, amount, bid=None, ask=None):
        func_x = lambda: self.exchange_x.order_buy(amount,
                                                   ask_for_coincheck=ask)
        func_y = lambda: self.exchange_y.order_sell(amount,
                                                    bid_for_coincheck=bid)

        return self._request(func_x, func_y)

    def order_buyy_sellx(self, amount, bid=None, ask=None):
        func_x = lambda: self.exchange_y.order_buy(amount,
                                                   ask_for_coincheck=ask)
        func_y = lambda: self.exchange_x.order_sell(amount,
                                                    bid_for_coincheck=bid)

        return self._request(func_x, func_y)
