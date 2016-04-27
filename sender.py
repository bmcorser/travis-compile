import platform
import os

import requests


def main():
    # TODO: Decide what to call files
    name = "{0}-{1}.tar.gz".format(platform.machine(), platform.system())
    files = {name: open('./release.tar.gz', 'rb')}
    resp = requests.post(os.environ['NGROK_URL'], files=files)
    assert resp.ok

if __name__ == '__main__':
    main()
