class Tick():
    def __init__(self, timestamp, bid, ask):
        self.timestamp = timestamp
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return "{} bid={} ask={}".format(self.timestamp, self.bid, self.ask)
