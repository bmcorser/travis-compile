import platform
from os import environ as env
import sys

import requests


def main(rust_name):
    system_aliases = {
        'Darwin': 'macosx',
        'Linux': 'linux',
        'Windows': 'windows'
    }
    system_name = system_aliases[platform.system()]
    name_fmt = (rust_name, system_name, platform.machine())
    name = "{0}-{1}-{2}.tar.gz".format(*name_fmt)
    files = {name: open('./release.tar.gz', 'rb')}
    resp = requests.post(env['NGROK_URL'], files=files)
    assert resp.ok

if __name__ == '__main__':
    rust_name = sys.argv[1]
    main(rust_name)
