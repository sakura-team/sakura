import os
if not os.getenv('UNIT_TEST'):
    # in normal mode, load configuration
    from sakura.daemon.conf import load_conf
    conf = load_conf()
os.environ['SAKURA_ENV'] = 'daemon'
