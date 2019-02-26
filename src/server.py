# coding: utf-8
import functools
import json
import os

import flask
import argparse
import yaml

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


def search_account(fn):
    def wrapper(login):
        try:
            account = Account.from_json(
                fn(login)
            )
            return flask.Response(
                response=json.dumps(account),
                mimetype='application/json',
            )
        except FileNotFoundError:
            return flask.Response(
                response=json.dumps({'error': f'Account "{login}" does not exist'}),
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
    with open(os.path.join(app.config['COALECTIVE']['data_dir'], f'{user.login}.json'), 'w') as file:
        file.write(json.dumps(user.to_dict()))
    return user.to_dict()


@app.route('/accounts/<login>', methods=('GET',))
@search_account
def handle_retrieve_user(login):
    """
    Returns account with given name.
    """
    with open(os.path.join(app.config['COALECTIVE']['data_dir'], f'{login}.json'), 'r') as file:
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

    DEFAULT_CONFIG = {
        'fmt': 'json',
    }

    CONFIG_FIELDS = (
        'data_dir',
        'fmt',
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()
    with open(args.config) as f:
        config = {
            **DEFAULT_CONFIG,
            **yaml.load(f.read()),
        }

    for k in config:
        if k not in CONFIG_FIELDS:
            print(f'Config {k} not expected, ignoring')

    if not os.path.isdir(config['data_dir']):
        raise RuntimeError(f'{config["data_dir"]} is not a directory')
    if not os.access(config['data_dir'], os.W_OK):
        raise RuntimeError(f'{config["data_dir"]} is not writeable')
    if config['fmt'] not in ('xml', 'json'):
        raise RuntimeError(f'{config["fmt"]} is unexpected format')

    app.config['COALECTIVE'] = config
    print(config)
    app.run(host='localhost', port=8080, debug=True)
