from sakura.client.opskeleton.tools import get_suffixes, join_blocks, fix_indent
from sakura.client.opskeleton.param import ComboParameter, NumericColumnSelection, FloatColumnSelection

TAB_DECL_PATTERN = '''\
self.register_tab('%(tab_desc)s', '%(tab_html_file)s')\
'''

CSS_LINK_PATTERN = '''\
<link rel="stylesheet" type="text/css" href="%(url)s">\
'''

JS_LINK_PATTERN = '''\
<script src="%(url)s"></script>
'''

TAB_HTML_PATTERN = '''\
<!DOCTYPE html>

<html style="height:100%%;">
    <head>
        <meta charset="UTF-8" />
        <script src="/js/sakura-common.js"></script>
        <script src="/js/sakura-operator.js"></script>

        <!-- operator-specific includes ... -->
        %(links)s

        <!-- ... done. -->
    </head>
    <body style="height:100%%;" onload="init_%(tab_id)s()">
        %(body)s
    </body>
</html>
'''

class Tab:
    def __init__(self, tab_desc, tab_identifier):
        self.desc = tab_desc
        self.tab_identifier = tab_identifier
        self.html_file = tab_identifier + '.html'
        self.css_file = tab_identifier + '.css'
        self.js_file = tab_identifier + '.js'
    @property
    def decl_pattern(self):
        return TAB_DECL_PATTERN % dict(
            tab_desc = self.desc,
            tab_html_file = self.html_file
        )
    @property
    def custom_attributes(self):
        return ''

    @property
    def custom_method(self):
        return ''

    @property
    def custom_imports(self):
        return ()

    def get_custom_css_links(self):
        return ()

    def get_custom_js_links(self):
        return ()

    def generate_files(self, op_dir):
        css_dir = op_dir / 'css'
        css_dir.mkdir(exist_ok=True)
        js_dir = op_dir / 'js'
        js_dir.mkdir(exist_ok=True)
        with (op_dir / self.html_file).open('w') as html_f:
            print(self.generate_html_file(), file=html_f)
        with (css_dir / self.css_file).open('w') as css_f:
            print(self.generate_css_file(), file=css_f)
        with (js_dir / self.js_file).open('w') as js_f:
            print(self.generate_js_file(), file=js_f)

    def generate_html_file(self):
        css_links = [ 'css/' + self.css_file ] + list(self.get_custom_css_links())
        js_links = list(self.get_custom_js_links()) + [ 'js/' + self.js_file ]
        links = []
        links.extend(CSS_LINK_PATTERN % dict(url = url) for url in css_links)
        links.extend(JS_LINK_PATTERN % dict(url = url) for url in js_links)
        links = join_blocks(links, '\n', 8)
        body = fix_indent(8, self.generate_html_body())
        return TAB_HTML_PATTERN % dict(
            links = links,
            tab_id = self.tab_identifier,
            body = body
        )

DEFAULT_TAB_CSS = '''\
.infobox {
    padding: 6px 8px;
    font: 14px/16px Arial, Helvetica, sans-serif;
    background: white;
    background: rgba(255,255,255,0.8);
    box-shadow: 0 0 15px rgba(0,0,0,0.2);
    border-radius: 5px;
    text-align: center;
    color: #777;
}
'''

DEFAULT_TAB_JS_PATTERN = '''\
function init_%(tab_id)s() {
    console.log("%(html_file)s loaded");
}
'''

class DefaultTab(Tab):
    def generate_html_body(self):
        return '<div class="infobox">This is %s</div>' % self.html_file
    def generate_css_file(self):
        return DEFAULT_TAB_CSS
    def generate_js_file(self):
        return DEFAULT_TAB_JS_PATTERN % dict(
            tab_id = self.tab_identifier,
            html_file = self.html_file
        )

COUNTER_TAB_CUSTOM_ATTRIBUTES = '''\
self.chunks_iterator = None
self.count = 0
'''

COUNTER_TAB_CUSTOM_CODE = '''\
# This function is called when fire_event() is called on javascript
# side. The return value of this function becomes the return value
# of this fire_event() call.
# This sample function reads input stream and counts its records.
def handle_event(self, ev_type, time_credit):
    if not self.%(input_name)s.connected():
        return { 'issue': 'NO DATA: Input is not connected.' }
    # The javascript code calls us with ev_type value 'count_start'
    # or 'count_continue'. In the 1st case we (re-)build the iterator,
    # otherwise we just continue iterating.
    if ev_type == 'count_start':
        # start iterating on input
        self.chunks_iterator = self.input_plug.source.chunks()
        self.count = 0
    # read input stream until it ends or time credit is expired
    deadline = time() + time_credit
    for chunk in self.chunks_iterator:
        self.count += len(chunk)
        if time() > deadline:
            # stop because of deadline
            return { 'count': self.count, 'ended': False }
    # stop because of the end of stream
    return { 'count': self.count, 'ended': True }
'''

COUNTER_TAB_HTML_CODE = '''\
<div id="infobox" class="infobox"></div>
'''

COUNTER_TAB_JS_CODE = '''\
REFRESH_DELAY = 0.3;

function handle_operator_response(result) {
    let icon;
    if ('issue' in result)
    {
        infobox_update({ 'icon': 'alert', 'text': result.issue });
        return;
    }
    if (result.ended)
    {   // the whole input stream was read
        icon = 'check';
    }
    else {
        icon = 'hourglass';
        // request python code for more complete data,
        // while we refresh the screen
        request_update('count_continue');
    }
    infobox_update({ "icon": icon, 'text': 'input has ' + result.count + ' rows' });
}

function request_update(ev_type) {
    sakura.apis.operator.fire_event(
            ev_type, REFRESH_DELAY).then(
            handle_operator_response);
}

function infobox_update(props) {
    let infobox = document.querySelector("#infobox");
    infobox.innerHTML = props.text + ' ' +
                '<span class="glyphicon glyphicon-' + props.icon + '"></span>';
};

function init_%(tab_id)s() {
    request_update('count_start');
    console.log("%(html_file)s loaded");
}
'''

class CounterTab(Tab):
    def __init__(self, op_input, *args):
        Tab.__init__(self, *args)
        self.op_input = op_input
    @staticmethod
    def instanciate(inputs, params, args):
        if len(inputs) > 0:
            return CounterTab(inputs[0], *args)
    @property
    def custom_attributes(self):
        return COUNTER_TAB_CUSTOM_ATTRIBUTES
    @property
    def custom_method(self):
        return (COUNTER_TAB_CUSTOM_CODE % dict(
            input_name = self.op_input.name
        )).strip()
    @property
    def custom_imports(self):
        return ('from time import time',)
    def get_custom_css_links(self):
        return ("/webcache/cdnjs/twitter-bootstrap/3.3.7/css/bootstrap.min.css",)
    def generate_html_body(self):
        return COUNTER_TAB_HTML_CODE
    def generate_css_file(self):
        return DEFAULT_TAB_CSS
    def generate_js_file(self):
        return COUNTER_TAB_JS_CODE % dict(
            tab_id = self.tab_identifier,
            html_file = self.html_file
        )

def yield_tabs(num, factory):
    if num == 0:
        return
    suffixes = get_suffixes(num)
    for i in range(num):
        suffix = suffixes[i]
        tab_identifier = 'tab' + suffix
        tab_desc = 'Tab' + suffix.replace('_', ' ')
        yield factory(tab_desc, tab_identifier)

class TabFactory:
    def __init__(self, inputs, params):
        self.inputs = inputs
        self.params = params
        self.possible_types = [ CounterTab ]
    def __call__(self, *args):
        for cls in self.possible_types.copy():
            instance = cls.instanciate(self.inputs, self.params, args)
            if instance is not None:
                self.possible_types.remove(cls)
                return instance
        # by default return this one
        return DefaultTab(*args)

def generate_tabs(num, inputs, params):
    factory = TabFactory(inputs, params)
    return list(yield_tabs(num, factory))

def generate_tabs_declaration(tabs):
    if len(tabs) == 0:
        return []
    lines = [ "# tabs" ]
    lines.extend(t.decl_pattern.strip() for t in tabs)
    custom_attributes_code = list(t.custom_attributes.strip() for t in tabs)
    if max(len(c) for c in custom_attributes_code) > 0:
        lines.append("# custom attributes")
        lines.extend(custom_attributes_code)
    return lines
