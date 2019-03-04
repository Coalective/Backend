import os
import json

from exceptions import ValidationError


__all__ = ('Account', 'User', 'Room', 'MailingList')


class Account(dict):
    name: str

    ALLOWED_FIELDS = (
        'name',
        'type',
        'image',
        'contacts',
        'login',
    )

    REQUIRED_FIELDS = (
        'name',
        'type',
        'login',
    )

    FIELDS = (
        'name',
        'type',
        'image',
        'contacts',
        'login',
    )

    def __init__(self, name, login, account_type, image='', contacts=None,):
        super().__init__()

        if not isinstance(name, str):
            raise ValidationError(f'Invalid name type, expected string, got {type(name)}')

        if contacts is None:
            contacts = ['rt']

        self.contacts = contacts
        self.name = name
        self.login = login
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
            if key not in cls.ALLOWED_FIELDS:
                raise ValidationError(f'Field "{key}" is not allowed.')

    @classmethod
    def validate_unique_login(cls, deserialized_json):
        # Check if user try to create existing one.
        login = deserialized_json['login']
        if os.path.exists(f'{login}.json'):
            raise ValidationError(f'{cls.__name__} "{login}" already exists.')

    @classmethod
    def from_valid_dict(cls, valid_dict):
        return cls(
            name=valid_dict.get('name'),
            login=valid_dict.get('login'),
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

        cls.validate_unique_login(deserialized_json)

        return cls.from_valid_dict(deserialized_json)

    def to_dict(self):
        return {
            field: getattr(self, field)
            for field in self.FIELDS
        }


class User(Account):

    ALLOWED_FIELDS = (
        'name',
        'image',
        'contacts',
        'login',
    )

    REQUIRED_FIELDS = (
        'name',
        'login',
    )

    FIELDS = (
        'name',
        'image',
        'contacts',
        'login',
        'type',
    )

    def __init__(self, name, login, image='', contacts=None):
        super().__init__(name, login, account_type='1', image=image, contacts=contacts)

    @classmethod
    def from_valid_dict(cls, valid_dict):
        return cls(
            name=valid_dict.get('name'),
            login=valid_dict.get('login'),
            contacts=valid_dict.get('contacts'),
            image=valid_dict.get('image'),
        )


class Room(Account):

    ALLOWED_FIELDS = (
        'name',
        'image',
        'contacts',
        'login',
    )

    REQUIRED_FIELDS = (
        'name',
        'login',
    )

    FIELDS = (
        'name',
        'image',
        'contacts',
        'login',
        'type',
    )

    def __init__(self, name, login, image='', contacts=None):
        super().__init__(name, login, account_type='2', image=image, contacts=contacts)


class MailingList(Account):

    ALLOWED_FIELDS = (
        'name',
        'image',
        'contacts',
        'login',
    )

    REQUIRED_FIELDS = (
        'contacts',
        'login',
    )

    FIELDS = (
        'name',
        'image',
        'contacts',
        'login',
        'type',
    )

    def __init__(self, login, name='', image='', contacts=None):
        if not contacts:
            raise ValidationError(f'Invalid contacts value: {contacts}')

        if not name:
            name = 'no_name'

        super().__init__(name, login, account_type='3', image=image, contacts=contacts)

    @classmethod
    def from_valid_dict(cls, valid_dict):
        return cls(
            name=valid_dict.get('name'),
            login=valid_dict.get('login'),
            contacts=valid_dict.get('contacts'),
            image=valid_dict.get('image')
        )
