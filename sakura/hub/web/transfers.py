import random

class Transfer:
    def __init__(self):
        self.transfer_id = random.getrandbits(32)
        self.percent = 0
    def get_percent(self):
        return self.percent
    def notify_estimate(self, val_done, val_target):
        if val_target == 0:     # unknown
            return -1
        percent = int(val_done * 100 / val_target)
        if percent == 0:
            percent = 1
        if percent >= 100:
            percent = 99
        self.percent = percent
    def notify_done(self):
        self.percent = 100
