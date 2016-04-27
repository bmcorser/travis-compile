import os
import shutil
import socket
import subprocess
import sys
import uuid

import requests


GITHUB_API = 'https://api.github.com'
RUST_DIR = 'rust-src'


def free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    del(sock)
    return port


def get_ngrok_url(port):
    url = "http://localhost:{0}/api/tunnels/receiver".format(port)
    while True:
        try:
            resp = requests.get(url)
            return resp.json()['public_url']
        except (requests.ConnectionError, KeyError):
            pass


def start_ngrok(for_port):
    api_port = free_port()
    dot = os.path.dirname(os.path.realpath(__file__))
    ngrok_path = os.path.join(dot, 'ngrok')
    config = 'ngrok.yml'
    template(config, api_port)
    process = subprocess.Popen([ngrok_path, 'http', str(for_port), '-config', config])
    try:
        return get_ngrok_url(api_port)
    finally:
        process.terminate()


def checkout(branch, new=False):
    cmd = ['git', 'checkout']
    if new:
        cmd.append('-b')
    cmd.append(branch)
    subprocess.check_call(cmd)


def clean():
    checkout('test')
    subprocess.check_call([
        'git', 'reset', '--hard', 'HEAD'
    ])
    subprocess.check_call([
        'git', 'clean', '-fd',
    ])


def commit():
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', 'Compile me!'])


def make_pr(user, token, branch):
    url = '/'.join(GITHUB_API, 'repos/bmcorser/travis-compile/pulls')
    pr = {
        'title': 'Amazing new feature',
        'body': 'Please pull this in!',
        'head': "{0}:{1}".format(user, branch),
        'base': 'master'
    }
    resp = requests.post(url, auth=(user, token), json=pr, timeout=2)
    assert resp.ok
    return resp.json()


def template(name, *fmt_args):
    with open("{0}.template".format(name), 'r') as fh:
        template_string = fh.read()
    with open(name, 'w') as fh:
        fh.write(template_string.format(*fmt_args))


def main(cargo_path, user, token):
    clean()
    branch = uuid.uuid4().hex
    checkout(branch, new=True)
    shutil.copytree(cargo_path, './rust-src')
    receiver_port = free_port()
    import ipdb;ipdb.set_trace()
    ngrok_url = start_ngrok(receiver_port)
    template('.travis.yml', ngrok_url)
    commit()
    make_pr(user, token, branch)

if __name__ == '__main__':
    cargo_path, user, token = sys.argv[1:]
    main(cargo_path, user, token)
