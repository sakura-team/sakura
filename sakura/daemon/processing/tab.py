# Tab implementation.
class Tab(object):
    def __init__(self, label, js_path):
        self.label = label
        self.js_path = js_path

    def get_info_serializable(self):
        info = dict(
            label = self.label,
            js_path = self.js_path
        )
        return info
