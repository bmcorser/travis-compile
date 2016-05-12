import os
import requests

import util


def get_ngrok_url(port):
    url = "http://localhost:{0}/api/tunnels/command_line".format(port)
    while True:
        try:
            resp = requests.get(url)
            return resp.json()['public_url']
        except (requests.ConnectionError, KeyError):
            pass


def start_ngrok(for_port):
    '''
    Start ngrok on the passed port and return the running process and the
    public URL for the started ngrok server
    '''
    api_port = util.free_port()
    dot = os.path.dirname(os.path.realpath(__file__))
    ngrok_path = os.path.join(dot, 'ngrok')
    config = 'ngrok.yml'
    util.template(config, api_port)
    process = util.run_silent([
        ngrok_path, 'http', str(for_port), '-config', config,
    ])
    return process, get_ngrok_url(api_port)
