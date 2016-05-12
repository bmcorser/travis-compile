import json
import os
import shutil
import subprocess
import sys
import uuid

import requests

import util


GITHUB_API = 'https://api.github.com'
RUST_DIR = 'rust-src'


def checkout(branch, new=False):
    cmd = ['git', 'checkout']
    if new:
        cmd.append('-b')
    cmd.append(branch)
    subprocess.check_call(cmd)


def clean():
    checkout('master')
    '''
    subprocess.check_call([
        'git', 'reset', '--hard', 'HEAD'
    ])
    subprocess.check_call([
        'git', 'clean', '-fd',
    ])
    '''


def commit():
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', 'Ok then!'])


def make_pr(user, token, branch):
    subprocess.check_call(['git', 'push', 'origin', branch])
    url = '/'.join([GITHUB_API, "repos/{0}/pulls".format(user_repo)])
    pr = {
        'title': 'Compile me!',
        'body': '',
        'head': "{0}:{1}".format(user, branch),
        'base': 'master'
    }
    user, _ = user_repo.split('/')
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
        print(' '.join(cmd))
        # subprocess.check_call(cmd)


def main(cargo_path, user_repo, token, ngrok_proc):
    clean()
    branch = "compile-{0}".format(uuid.uuid4().hex[:7])
    rust_src = 'rust-src'
    try:
        checkout(branch, new=True)
        shutil.copytree(cargo_path, rust_src)
        try:
            shutil.rmtree(os.path.join(rust_src, '.git'))
        except Exception as exc:
            print(exc)
        manifest_path = os.path.join(rust_src, 'Cargo.toml')
        cargo_manifest = json.loads(subprocess.check_output([
            'cargo', 'read-manifest',
            "--manifest-path={0}".format(manifest_path)
        ]).decode('utf8'))
        receiver_port = util.free_port()
        ngrok_proc, ngrok_url = util.start_ngrok(receiver_port)
        print("Requesting pubkey for {0} ...".format(user_repo))
        pubkey_url = "https://api.travis-ci.org/repos/{0}/key".format(user_repo)
        pubkey_str = requests.get(pubkey_url).json()['key']
        import ipdb;ipdb.set_trace()
        util.template('.travis.yml', cargo_manifest['name'], ngrok_url)
        util.template('appveyor.yml', cargo_manifest['name'], ngrok_url)
        commit()
        make_pr(user_repo, token, branch)
        receiver = subprocess.Popen([
            'python', 'receiver.py',
            str(receiver_port), '6',
        ])
        receiver.wait()
    # except Exception as exc:
    #     import ipdb;ipdb.set_trace()
    #     print(exc)
    finally:
        clean_up(branch)

if __name__ == '__main__':
    subprocess.check_call(['./install-ngrok.sh'])
    cargo_path, user_repo, token = sys.argv[1:]
    ngrok_proc = None
    try:
        main(cargo_path, user_repo, token, ngrok_proc)
    finally:
        if ngrok_proc:
            ngrok_proc.terminate()
