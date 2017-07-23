# all researches
RESEARCHES = []

# research info equivalent to research in js code
class Research:
    
    def __init__(self, rid, roi, dateStart, dateEnd):
        self.rid = rid
        self.roi = roi
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        RESEARCHES.append(self)

    