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

def ref_sha(ref):
    cmd = ['git', 'rev-parse', ref]
    return subprocess.check_output(cmd).strip().decode('utf8')


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


def make_pr(user_repo, token, branch):
    user, _ = user_repo.split('/')
    subprocess.check_call(['git', 'push', 'origin', branch])
    url = '/'.join([GITHUB_API, "repos/{0}/pulls".format(user_repo)])
    pr = {
        'title': 'Compile me!',
        'body': '',
        # 'head_sha': ref_sha('HEAD'),
        # 'base_sha': ref_sha('origin/master'),
        'head': "{0}:{1}".format(user, branch),
        'base': 'master'
    }
    import ipdb;ipdb.set_trace()
    resp = requests.post(url, auth=(user, token), json=pr, timeout=5)
    if not resp.ok:
        raise Exception(resp)
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


def main(cargo_path, user_repo, github_token, appveyor_token, ngrok_proc):
    clean()
    branch = "compile-{0}".format(uuid.uuid4().hex[:7])
    rust_src = 'rust-src'
    manifest_path = os.path.join(rust_src, 'Cargo.toml')
    cargo_manifest = json.loads(subprocess.check_output([
        'cargo', 'read-manifest',
        "--manifest-path={0}".format(manifest_path)
    ]).decode('utf8'))
    try:
        print('Starting ngrok ...')
        receiver_port = util.free_port()
        ngrok_proc, ngrok_url = util.start_ngrok(receiver_port)

        print('Encrypting ngrok URL for Travis ...')
        travis_url = util.travis_encrypt(user_repo, "NGROK_URL={0}".format(ngrok_url))
        util.template('.travis.yml', cargo_manifest['name'], travis_url)

        print('Encrypting ngrok URL for Appveyor ...')
        appveyor_url = util.appveyor_encrypt(appveyor_token, ngrok_url)
        util.template('appveyor.yml', cargo_manifest['name'], appveyor_url)

        '''
        print('Committing your Rust source to a new branch ...')
        checkout(branch, new=True)
        shutil.copytree(cargo_path, rust_src)
        try:
            shutil.rmtree(os.path.join(rust_src, '.git'))
        except Exception as exc:
            print(exc)
        '''
        commit()

        print('Making PR on GitHub ...')
        make_pr(user_repo, github_token, branch)

        print('Starting the receiver server ...')
        receiver = subprocess.Popen([
            'python', 'receiver.py',
            str(receiver_port), '6',
        ])

        print('Now we wait.')
        receiver.wait()
    except Exception as exc:
        import ipdb;ipdb.set_trace()
        print(exc)
    finally:
        clean_up(branch)

if __name__ == '__main__':
    subprocess.check_call(['./install-ngrok.sh'])
    cargo_path, user_repo, github_token, appveyor_token = sys.argv[1:]
    ngrok_proc = None
    try:
        main(cargo_path, user_repo, github_token, appveyor_token, ngrok_proc)
    finally:
        if ngrok_proc:
            ngrok_proc.terminate()
