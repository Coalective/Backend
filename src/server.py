# coding: utf-8

import flask

app = flask.Flask(__name__)


@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/about')
def about():
    return 'Hello, About!'


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
