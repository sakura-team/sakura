import os
if not os.getenv('UNIT_TEST'):
    # in normal mode, load configuration
    from sakura.hub.conf import load_conf
    conf = load_conf()
