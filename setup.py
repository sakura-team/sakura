from setuptools import setup
from pathlib import Path
from pkg_resources import resource_filename
import sys

if not sys.version_info[0] == 3:
    sys.exit("Sorry, only Python 3 is supported.")

proj_dir = Path(resource_filename(__name__, 'setup.py')).resolve().parent
def find_packages():
    return sorted(set(str(f.parent.relative_to(proj_dir)) for f in proj_dir.glob('sakura/**/*.py')))

def iter_data_files(dirname):
    # iterate over files of web_interface
    for d in sorted(set(f.parent.relative_to(proj_dir) for f in proj_dir.glob(dirname + '/**/*'))):
        files = list(str(f) for f in d.iterdir() if f.is_file() and not str(f).startswith('gitignore'))
        if len(files) == 0:
            continue
        dest_path = 'sakura/' + str(d)
        yield (dest_path, files)

setup(
    name = 'sakura-py',
    version = '0.1',
    packages = find_packages(),
    package_dir = {'sakura-py': 'sakura'},
    data_files = list(iter_data_files('web_interface')) + list(iter_data_files('operators')),
    install_requires = ['gevent', 'gevent-websocket', 'bottle', 'numpy', 'psycopg2-binary', 'pony==0.7.2', 'websocket-client'],
    author = 'Etienne Duble',
    author_email = 'etienne.duble@imag.fr',
    keywords = 'sakura data-processing research capitalization',
    license = 'BSD',
    url = 'https://github.com/sakura-team/sakura',
    description = 'Sakura platform installation files.',
    entry_points = dict(
        console_scripts = ['sakura-hub = sakura.hub.hub:run', 'sakura-daemon = sakura.daemon.daemon:run']
    ),
    include_package_data = True
)
