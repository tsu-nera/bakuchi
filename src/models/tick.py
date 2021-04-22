class Tick():
    def __init__(self, exchange_id, timestamp, bid, ask):
        self.exchange_id = exchange_id
        self.timestamp = timestamp
        self.bid = float(bid)
        self.ask = float(ask)

    def __str__(self):
        return "{} bid={} ask={}".format(self.timestamp, self.bid, self.ask)
