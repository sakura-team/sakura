class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context
    
    def list_daemons(self, *args, **kwargs):
        daemons = self.context.list_daemons()
        print("list_daemons:", args, kwargs, '->', daemons)
        return daemons
    
    def list_operators_classes(self):
        return opcl
    
    def instantiate_operator(self, *args, **kwargs):
        id = args[0]
        return ("not yet")
    
###########################MIKE#############################
svgs = []
opcl = []

def generate_icon():
    global index
    color = ['yellow', 'blue', 'green', 'white', 'grey', 'pink', 'red', 'purple']
    if not 'index' in globals():
        index = 0
    else:
        index = (index+1)%len(color)
    return '<svg width="38" height="38"><circle cx="19" cy="19" r="17" stroke="black" stroke-width="2" fill="'+color[index]+'" /></svg>'


for i in range(20):
    svgs.append(generate_icon())

#id, name, daemon, [tags], svg code, nb inputs, nb outputs
opcl.append({'id': 0, 'name': "AllData", 'daemon': "geotweet", 'tags': ["data", "geotweet", "bigdata"], 'svg': svgs[0], 'inputs': 0, 'outputs': 4})
opcl.append({'id': 1, 'name': "Mean", 'daemon': "geotweet", 'tags': ["mean", "geotweet", "bigdata"], 'svg': svgs[1], 'inputs': 1, 'outputs': 1})
opcl.append({'id': 2, 'name': "Select", 'daemon': "sakura", 'tags': ["select", "sakura", "management"], 'svg': svgs[2], 'inputs': 1, 'outputs': 0})
opcl.append({'id': 3, 'name': "Mean", 'daemon': "sakura", 'tags': ["mean", "sakura", "management"], 'svg': svgs[3], 'inputs': 4, 'outputs': 0})
opcl.append({'id': 4, 'name': "Tototututiti", 'daemon': "sakura", 'tags': ["toto", "sakura", "weird"], 'svg': svgs[4], 'inputs': 1, 'outputs': 4})
opcl.append({'id': 5, 'name': "Visu", 'daemon': "IIHM", 'tags': ["visualisation", "IIHM"], 'svg': svgs[5], 'inputs': 2, 'outputs': 3})
opcl.append({'id': 6, 'name': "Acp", 'daemon': "IIHM", 'tags': ["acp", "statistics", "IIHM"], 'svg': svgs[6], 'inputs': 1, 'outputs': 1})






############################################################