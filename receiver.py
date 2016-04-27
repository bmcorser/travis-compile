import sys
from flask import Flask, request
from werkzeug import secure_filename

app = Flask(__name__)
N = None


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global N
    if request.method == 'POST':
        for name in request.files:
            file = request.files[name]
            filename = secure_filename(file.filename)
            file.save(filename)
    N -= 1
    if N < 1:
        request.environ.get('werkzeug.server.shutdown')()
    return 'ok'


if __name__ == '__main__':
    port, n = map(int, sys.argv[1:])
    N = n
    app.run(port=port, debug=True)
