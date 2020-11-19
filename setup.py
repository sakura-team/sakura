import sys
from pathlib import Path
from pkg_resources import resource_filename

if not sys.version_info[0] == 3:
    sys.exit("Sorry, only Python 3 is supported.")

missing = []

try:
    from setuptools import setup
except:
    missing.append("setuptools")

if len(missing) > 0:
    sys.exit("Sorry, your python environment is not ready: install %s with pip first." % \
             " and ".join(missing))

proj_dir = Path(resource_filename(__name__, 'setup.py')).resolve().parent
def find_packages():
    return sorted(set(str(f.parent.relative_to(proj_dir)) for f in proj_dir.glob('sakura/**/*.py')))

def iter_data_files(dirname):
    # iterate over files of web_interface
    for d in sorted(set(f.parent.relative_to(proj_dir) for f in proj_dir.glob(dirname + '/**/*'))):
        files = list(str(f) for f in d.iterdir() \
                                if f.is_file() \
                                and not f.name.startswith('gitignore'))
        if len(files) == 0:
            continue
        dest_path = 'sakura/' + str(d)
        yield (dest_path, files)

setup(
    name = 'sakura-py',
    version = '0.9.3',
    packages = find_packages(),
    package_dir = {'sakura-py': 'sakura'},
    data_files = list(iter_data_files('web_interface')) + list(iter_data_files('operators')),
    setup_requires = [ 'wheel' ],
    install_requires = [ 'wheel', 'gevent', 'bottle', 'numpy', 'websocket-client', 'geojson' ],
    extras_require = {
        'hub': [ 'pony==0.7.6', 'gevent-websocket' ],
        'daemon': [ 'cffi', 'psycopg2-binary', 'pillow-simd', 'cython', 'pyopengl', 'pyopengl-accelerate', 'requests' ]
    },
    author = 'Etienne Duble',
    author_email = 'etienne.duble@imag.fr',
    keywords = 'sakura data-processing research capitalization',
    license = 'BSD',
    url = 'https://github.com/sakura-team/sakura',
    description = 'Sakura platform installation files.',
    entry_points = dict(
        console_scripts = [ 'sakura-hub = sakura.hub.hub:run [hub]',
                            'sakura-hub-sendmail = sakura.hub.sendmail:run [hub]',
                            'sakura-daemon = sakura.daemon.daemon:run [daemon]',
                            'sakura-encode-password = sakura.common.password:password_encoder_tool',
                            'sakura-shell = sakura.client.shell:run',
                            'sakura-op-skeleton = sakura.client.opskeleton:run',
                            'sakura-sandbox = sakura.client.sandbox:run' ]
    ),
    include_package_data = True
)
