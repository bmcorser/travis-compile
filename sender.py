import platform
import os
import sys

import requests


def main(rust_name):
    system_name = {'Darwin': 'macosx', 'Linux': 'linux'}[platform.system()]
    arch = os.environ['ARCH']
    name = "{0}-{1}-{2}.tar.gz".format(rust_name, system_name, arch)
    files = {name: open('./release.tar.gz', 'rb')}
    resp = requests.post(os.environ['NGROK_URL'], files=files)
    assert resp.ok

if __name__ == '__main__':
    rust_name = sys.argv[1]
    main(rust_name)
