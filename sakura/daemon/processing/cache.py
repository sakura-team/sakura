class Cache:
    def __init__(self, size):
        self.size = size
        self.per_item = {}
        self.per_info = {}
        self.per_date = []
    def get(self, *info):
        if info in self.per_info:
            return self.per_info[info]
        return None
    def forget(self, item):
        info = self.per_item[item]
        self.per_date.remove(item)
        del self.per_item[item]
        del self.per_info[info]
    def save(self, item, *info):
        if item in self.per_item:
            # remove previous info about item
            old_info = self.per_item[item]
            del self.per_info[old_info]
            # remove item from per_date, it
            # will be appended below
            self.per_date.remove(item)
        if info in self.per_info:
            # remove previous item linked to info
            old_item = self.per_info[info]
            del self.per_item[old_item]
            self.per_date.remove(old_item)
        if len(self.per_date) == self.size:
            # cache is full, drop oldest entry
            oldest_item = self.per_date[0]
            oldest_info = self.per_item[oldest_item]
            assert oldest_info in self.per_info, \
                        '********* cache coherency issue.'
            del self.per_item[oldest_item]
            del self.per_info[oldest_info]
            self.per_date = self.per_date[1:]
        # record entry for this item
        self.per_item[item] = info
        self.per_info[info] = item
        # update item position in self.per_date
        self.per_date.append(item)
        assert len(self.per_item) == len(self.per_info), \
                        '********* cache len issue.'
