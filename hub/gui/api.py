class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context
    
    def list_daemons(self, *args, **kwargs):
        daemons = self.context.list_daemons()
        print("list_daemons:", args, kwargs, '->', daemons)
        return daemons
    
    def list_operators_classes(self):
        from random import randrange
        global svgs
        
        def generate_icon():
            color = ['yellow', 'blue', 'green', 'white', 'grey', 'pink', 'red', 'purple']
            return '<svg width="38" height="38"><circle cx="19" cy="19" r="17" stroke="black" stroke-width="2" fill="'+color[randrange(0,len(color))]+'" /></svg>'
        
        if not 'svgs' in globals():
            svgs = []
            for i in range(20):
                svgs.append(generate_icon())
        
        opcl = []
        opcl.append([0, "AllData", "geotweet", ["data", "geotweet", "bigdata"], svgs[0]])
        opcl.append([1, "Mean", "geotweet", ["mean", "geotweet", "bigdata"], svgs[1]])
        opcl.append([2, "Select", "sakura", ["select", "sakura", "management"], svgs[2]])
        opcl.append([3, "Mean", "sakura", ["mean", "sakura", "management"], svgs[3]])
        opcl.append([4, "Toto", "sakura", ["toto", "sakura", "weird"], svgs[4]])
        opcl.append([5, "Visu", "IIHM", ["visualisation", "IIHM"], svgs[5]])
        opcl.append([6, "Acp", "IIHM", ["acp", "statistics", "IIHM"], svgs[6]])
        return opcl