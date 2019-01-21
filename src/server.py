# coding: utf-8
import json
import os
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


def search_file(fn):
    def wrapper(*args, **kwargs):
        try:
            user_data = fn(*args, **kwargs)
            return flask.Response(
                response=user_data,
                mimetype='application/json',
            )
        except FileNotFoundError as e:
            return flask.Response(
                response=json.dumps({'error': 'User does not exist'}),
                status=404,
                mimetype='application/json',
            )
    return wrapper


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
    def check_user_input_name(cls, deserialized_json):
        # Check if user try to create existing one.
        name = deserialized_json['name']
        if os.path.exists(name + '.json'):
            raise ValidationError(f'User "{name}" already exists.')

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

        cls.check_user_input_name(deserialized_json)

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
    user_data_json = User.from_json(flask.request.data).__dict__
    file = open(user_data_json['name'] + '.json', 'w')
    file.write(json.dumps(user_data_json))
    return user_data_json


@app.route('/accounts/<string:name>', methods=('GET', ))
@search_file
def handle_retrieve_account(name):
    """
    Returns account with given name.
    """
    file = open(name + '.json', 'r')
    return file.read()


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
