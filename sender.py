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
    name = "{0}-{1}-{2}.tar.gz".format(rust_name, system_name, env['ARCH'])
    files = {name: open('./release.tar.gz', 'rb')}
    resp = requests.post(env['NGROK_URL'], files=files)
    assert resp.ok

if __name__ == '__main__':
    rust_name = sys.argv[1]
    main(rust_name)
