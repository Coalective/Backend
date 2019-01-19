# coding: utf-8
import json

import flask

app = flask.Flask(__name__)


def json_response(fn):
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


class ValidationError(ValueError):
    """
    Raised ...
    """


class Account(dict):
    name: str

    FIELDS = (
        'name',
        'type',
        'image',
        'contacts',
    )

    REQUIRED_FIELDS = (
        'name',
        'type',
    )

    def __init__(self, name, account_type, image='', contacts=None,):
        super().__init__()

        if not isinstance(name, str):
            raise ValidationError(f'Invalid name type, expected string, got {type(name)}')

        if contacts is None:
            contacts = ['rt']

        self.contacts = contacts
        self.name = name
        self.type = account_type
        self.image = image

    @classmethod
    def parse_json(cls, serialized_json):
        # Check if json is valid.
        try:
            return json.loads(serialized_json)
        except Exception as e:
            print(e)
            raise ValidationError('Invalid json.')

    @classmethod
    def check_user_input_type(cls, deserialized_json):
        # Check if deserialized_json is dict.
        if not isinstance(deserialized_json, dict):
            raise ValidationError('Invalid json type.')

    @classmethod
    def check_user_input_keys(cls, deserialized_json):
        # Check if deserialized_json only contains valid keys.
        for key in cls.REQUIRED_FIELDS:
            if key not in deserialized_json:
                raise ValidationError(f'Field "{key}" is required.')

        # Check if all the fields are allowed.
        for key in deserialized_json:
            if key not in cls.FIELDS:
                raise ValidationError(f'Field "{key}" is not allowed.')

    @classmethod
    def from_valid_dict(cls, valid_dict):
        return cls(
            name=valid_dict.get('name'),
            account_type=valid_dict.get('type'),
            contacts=valid_dict.get('contacts'),
            image=valid_dict.get('image'),
        )

    @classmethod
    def from_json(cls, data):
        """
        Returns Account instance built from json.

        :param data: json encoded data
        :type data: bytes
        """
        deserialized_json = cls.parse_json(data)

        cls.check_user_input_type(deserialized_json)

        cls.check_user_input_keys(deserialized_json)

        return cls.from_valid_dict(deserialized_json)


class User(Account):

    FIELDS = (
        'name',
        'image',
        'contacts',
    )

    REQUIRED_FIELDS = (
        'name',
    )

    def __init__(self, name, image='', contacts=None):
        super().__init__(name, account_type='1', image=image, contacts=contacts)

    @classmethod
    def from_valid_dict(cls, valid_dict):
        return cls(
            name=valid_dict.get('name'),
            contacts=valid_dict.get('contacts'),
            image=valid_dict.get('image'),
        )


@app.route('/new/user', methods=('POST', ))
@json_response
def handle_create_account():
    """
    Creates new account.
    """
    return User.from_json(flask.request.data).__dict__


@app.route('/accounts/<string:account_id>', methods=('GET', ))
def handle_retrieve_account(account_id):
    """
    Returns account with given ID.
    """
    a = User(account_id)
    return flask.Response(json.dumps(a.__dict__))


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
