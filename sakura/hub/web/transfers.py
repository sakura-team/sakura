import random
from sakura.hub.exceptions import TransferAborted

class Transfer:
    def __init__(self, context):
        self.transfer_id = random.getrandbits(32)
        self.percent = 0
        self.rows = 0
        self.bytes = 0
        self.status = 'waiting'
        self.aborted = False
        self.session_id = context.session.id
    def abort(self):
        self.aborted = True
    def get_status(self):
        return dict(
            percent = self.percent,
            rows = self.rows,
            bytes = self.bytes,
            status = self.status
        )
    def notify_status(self, rows_done, rows_target, bytes_done):
        if self.aborted:
            raise TransferAborted
        self.rows = rows_done
        self.bytes = bytes_done
        if rows_target == 0:     # unknown
            percent = -1
        else:
            percent = int(rows_done * 100 / rows_target)
        if percent == 0:
            percent = 1
        if percent >= 100:
            percent = 99
        self.percent = percent
        self.status = 'running'
    def notify_done(self):
        self.percent = 100
        self.status = 'done'
