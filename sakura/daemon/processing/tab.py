# Tab implementation.
class Tab(object):
    def __init__(self, label, html_path):
        self.label = label
        self.html_path = html_path

    def pack(self):
        info = dict(
            label = self.label,
            html_path = self.html_path
        )
        return info
