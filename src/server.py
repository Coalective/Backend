# coding: utf-8
import functools
import json
import flask

from exceptions import ValidationError
from models import *


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
            account = Account.from_json(
                fn(*args, **kwargs)
            )
        except FileNotFoundError:
            return flask.Response(
                response=json.dumps({'error': f'Account does not exist'}),
                status=404,
                mimetype='application/json',
            )

        try:
            return flask.Response(
                response=json.dumps(account),
                mimetype='application/json',
            )
        except FileNotFoundError:
            return flask.Response(
                response=json.dumps({'error': f'Account{account.login}does not exist'}),
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
    user = User.from_json(flask.request.data)
    with open(f'{user.login}.json', 'w') as file:
        file.write(json.dumps(user.to_dict()))
    return user.to_dict()


@app.route('/accounts/<login>', methods=('GET',))
@search_file
def handle_retrieve_user(login):
    """
    Returns account with given name.
    """
    with open(f'{login}.json', 'r') as file:
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
