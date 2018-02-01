from flask import jsonify

from app.api import api
from app.exceptions import ValidationError


def bad_request(message):
    """
    请求不可用
    """
    response = jsonify({'error': message, 'code': '400', 'data': ''})
    return response


def unauthorized(message):
    """
    请求未包含授权信息
    """
    response = jsonify({'error': message, 'code': '401', 'data': ''})
    return response


def forbidden(message):
    """
    无访问权限
    """
    response = jsonify({'error': message, 'code': '403', 'data': ''})
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
