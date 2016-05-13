import base64
import os
import socket
import subprocess

import requests
import rsa


def run_silent(cmd, can_fail=False, **overrides):
    'Run a command, but discard its output. Raise on error'
    with open(os.devnull, 'w') as devnull:
        kwargs = {
            'stdout': devnull,
            'stderr': devnull,
        }
        kwargs.update(overrides)
        try:
            return subprocess.Popen(cmd, **kwargs)
        except subprocess.CalledProcessError as exc:
            if can_fail:
                print(exc)
            else:
                raise


def template(name, *fmt_args):
    'The smallest templating library known to humankind'
    with open("{0}.template".format(name), 'r') as fh:
        template_string = fh.read()
    with open(name, 'w') as fh:
        fh.write(template_string.format(*fmt_args))


def free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    del(sock)
    return port


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
    process = run_silent([
        ngrok_path, 'http', str(for_port), '-config', config
    ])
    return process, get_ngrok_url(api_port)


def travis_encrypt(user_repo, value):
    pubkey_url = "https://api.travis-ci.org/repos/{0}/key".format(user_repo)
    pubkey_json = requests.get(pubkey_url).json()
    pubkey_str = pubkey_json['key'].replace('PUBLIC', 'RSA PUBLIC')

    # magic from http://stackoverflow.com/a/29707204/3075972
    pubkey_lines = pubkey_str.split('\n')
    pubkey_lines[1] = pubkey_lines[1][32:]
    pubkey_str = '\n'.join(pubkey_lines)

    pubkey = rsa.PublicKey.load_pkcs1(pubkey_str)
    return base64.b64encode(rsa.encrypt(value, pubkey))


def appveyor_encrypt(api_key, value):
    endpoint_url = 'https://ci.appveyor.com/api/account/encrypt'
    headers = {'Authorization': "Bearer {0}".format(api_key)}
    data = {'plainValue': value}
    return requests.post(endpoint_url, headers=headers, json=data).text
