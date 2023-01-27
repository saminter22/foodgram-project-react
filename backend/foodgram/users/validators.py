# users/validators.py
import re

from django.core import validators

USERNAME_ALLOWED_SYMBOLS = r'^[a-zA-Z0-9@.+-_]*$'


def check_username(value):
    """Проверка имени пользователя на символы [a-zA-Z0-9@.+-_] и не 'me'"""
    error_name_text = ''
    if value.strip().lower() == 'me':
        error_name_text = 'Имя пользователя "me" запрещено!'
    if not re.match(USERNAME_ALLOWED_SYMBOLS, value):
        error_name_text = ('В имени пользователя'
                           ' использованы запрещенные символы!')
    return error_name_text


def validate_username(value):
    """Проверяем значение имени пользователя на коректность"""
    error_string = check_username(value)
    if error_string:
        raise ValueError(error_string)
