import shutil
import socket
import subprocess
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

def ngrok_public_url(port):
    url = "http://localhost:{0}/api/tunnels/receiver".format(port)
    while True:
        try:
            resp = requests.get(url)
            return resp.json()['public_url']
        except (requests.ConnectionError, KeyError):
            pass

def ngrok_server():
    port = free_port()
    ngrok_api_port = free_port()
    ngrok_path = os.path.join(os.path.dirname(__file__), 'ngrok')
    config = 'ngrok.yml'
    template(config, port, ngrok_api_port)
    process = run_silent([ngrok_path, '-config', config])
    public_url = ngrok_public_url()
    yield public_url
    process.terminate()


def checkout(branch):
    subprocess.check_call([
        'git', 'checkout', '-b', branch
    ])

def clean():
    subprocess.check_call([
        'git', 'rm', '-rf', RUST_DIR
    ])

def commit():
    subprocess.check_call([
        'git', 'add', '.', RUST_DIR
    ])

def make_pr(auth, branch):
    url = os.path.join(constants.GITHUB_API, url)
    return requests.post(url, auth=auth, timeout=2)

def template(name, *fmt_args):
    with open("{0}.template".format(name), 'r') as fh:
        template_string = fh.read()
    with open(name, 'w') as fh:
        fh.write(template_string.format(*fmt_args))

def main(cargo_path, github_auth):
    branch = uuid.uuid4()
    checkout(branch)
    clean()
    shutil.copytree(cargo_path, './rust-src')
    with open('.travis.yml.template', 'r') as fh:
        travis_template = fh.read()
    with open('.travis.yml', 'r') as fh:
        fh.write(travis_template.format(
