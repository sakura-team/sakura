
class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context
    
    def list_daemons(self, *args, **kwargs):
        daemons = self.context.list_daemons()
        print("list_daemons:", args, kwargs, '->', daemons)
        return daemons
    
    def list_operators_classes(self):
        opcl = []
        opcl.append([0, "AllData", "geotweet", ["data", "geotweet", "bigdata"], "svg code1"])
        opcl.append([1, "Mean", "geotweet", ["mean", "geotweet", "bigdata"], "svg code2"])
        opcl.append([2, "Select", "sakura", ["select", "sakura", "management"], "svg code3"])
        opcl.append([3, "Visu", "IIHM", ["visualisation", "IIHM"], "svg code4"])
        return opcl