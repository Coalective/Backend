# coding: utf-8
import functools
import json
import flask

from .exceptions import ValidationError
from .models import *


app = flask.Flask(__name__)


def json_response(fn):
    @functools.wraps(fn)
    def _wrapper(*args, **kwargs):
        try:
            response_data = fn(*args, **kwargs)
            return flask.Response(
                response=json.dumps(response_data),
                mimetype='application/json',
            )
        except ValidationError as e:
            return flask.Response(
                response=json.dumps({'error': str(e)}),
                status=400,
                mimetype='application/json',
            )
    return _wrapper


def search_file(fn):
    def wrapper(*args, **kwargs):
        try:
            user_data = fn(*args, **kwargs)
            return flask.Response(
                response=user_data,
                mimetype='application/json',
            )
        except FileNotFoundError:
            return flask.Response(
                response=json.dumps({'error': 'User does not exist'}),
                status=404,
                mimetype='application/json',
            )
    return wrapper


@app.route('/new/user', methods=('POST', ))
@json_response
def handle_create_user():
    """
    Creates new account.
    """
    user_data_json = User.from_json(flask.request.data).__dict__
    name = user_data_json['name']
    with open(f'{name}.json', 'w') as file:
        file.write(json.dumps(user_data_json))
    return user_data_json


@app.route('/accounts/<string:name>', methods=('GET', ))
@search_file
def handle_retrieve_user(name):
    """
    Returns account with given name.
    """
    file = open(f'{name}.json', 'r')
    return file.read()


@app.route('/new/room', methods=('POST',))
@json_response
def handle_create_room():
    return Room.from_json(flask.request.data).__dict__


@app.route('/new/mailing_list', methods=('POST', ))
@json_response
def handle_create_mailing_list():
    return MailingList.from_json(flask.request.data).__dict__


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
