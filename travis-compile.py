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


def run_silent(cmd, can_fail=False, **overrides):
    'Run a command, but discard its output. Raise on error'
    with open(os.devnull, 'w') as DEVNULL:
        kwargs = {
            'stdout': DEVNULL,
            'stderr': DEVNULL,
        }
        kwargs.update(overrides)
        try:
            return subprocess.Popen(cmd, **kwargs)
        except subprocess.CalledProcessError as exc:
            if can_fail:
                pass
            else:
                raise


def get_ngrok_url(port):
    url = "http://localhost:{0}/api/tunnels/command_line".format(port)
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
    process = run_silent([ngrok_path, 'http', str(for_port), '-config', config])
    return process, get_ngrok_url(api_port)


def checkout(branch, new=False):
    cmd = ['git', 'checkout']
    if new:
        cmd.append('-b')
    cmd.append(branch)
    subprocess.check_call(cmd)


def clean():
    checkout('master')
    subprocess.check_call([
        'git', 'reset', '--hard', 'HEAD'
    ])
    subprocess.check_call([
        'git', 'clean', '-fd',
    ])


def commit():
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', 'Ok then!'])


def make_pr(user, token, branch):
    subprocess.check_call(['git', 'push', 'origin', branch])
    url = '/'.join([GITHUB_API, 'repos/bmcorser/travis-compile/pulls'])
    pr = {
        'title': 'Compile me!',
        'body': '',
        'head': "{0}:{1}".format(user, branch),
        'base': 'master'
    }
    resp = requests.post(url, auth=(user, token), json=pr, timeout=5)
    assert resp.ok
    return resp.json()


def clean_up(branch):
    cmds = (
        ['git', 'checkout', 'master'],
        ['git', 'branch', '-D', branch],
        ['git', 'push', 'origin', ":{0}".format(branch)],
    )
    for cmd in cmds:
        # print(' '.join(cmd))
        subprocess.check_call(cmd)


def template(name, *fmt_args):
    with open("{0}.template".format(name), 'r') as fh:
        template_string = fh.read()
    with open(name, 'w') as fh:
        fh.write(template_string.format(*fmt_args))


def main(cargo_path, user, token, ngrok_proc):
    clean()
    branch = "compile-{0}".format(uuid.uuid4().hex[:7])
    try:
        checkout(branch, new=True)
        shutil.copytree(cargo_path, './rust-src')
        receiver_port = free_port()
        rust_name = os.path.dirname(cargo_path).split(os.path.sep)[-1]
        ngrok_proc, ngrok_url = start_ngrok(receiver_port)
        template('.travis.yml', rust_name, ngrok_url)
        template('appveyor.yml', ngrok_url)
        commit()
        make_pr(user, token, branch)
        receiver = subprocess.Popen([
            'python', 'receiver.py',
            str(receiver_port), '4',
        ])
        receiver.wait()
    finally:
        clean_up(branch)

if __name__ == '__main__':
    cargo_path, user, token = sys.argv[1:]
    ngrok_proc = None
    try:
        main(cargo_path, user, token, ngrok_proc)
    finally:
        if ngrok_proc:
            ngrok_proc.terminate()
