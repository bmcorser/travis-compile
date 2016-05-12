import os
import socket
import subprocess

import requests


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
