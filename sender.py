import platform
import os

import requests


def main():
    # TODO: Decide what to call files
    name = "{0}-{1}".format(platform.machine(), platform.system())
    files = {name: open('./rust-src.tar.gz', 'rb')}
    r = requests.post(os.environ['NGROK_URL'], files=files)
