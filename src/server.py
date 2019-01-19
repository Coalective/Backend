# coding: utf-8

import flask

app = flask.Flask(__name__)


@app.route('/new/account', methods=('POST', ))
def handle_create_account():
    """
    Creates new account.
    """
    raise RuntimeError('not yet')


@app.route('/accounts/<uuid:account_id>', methods=('GET', ))
def handle_retrieve_account(account_id):
    """
    Returns account with given ID.
    """
    return account_id


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
