from flask import jsonify

from app.api import api
from app.exceptions import ValidationError


def bad_request(message):
    """
    请求不可用
    """
    return jsonify({'error': message, 'code': '400', 'data': ''})


def unauthorized(message):
    """
    请求未包含授权信息
    """
    return jsonify({'error': message, 'code': '401', 'data': ''})


def forbidden(message):
    """
    无访问权限
    """
    return jsonify({'error': message, 'code': '403', 'data': ''})


def response(data='success'):
    """
    请求成功
    """
    return jsonify({'error': '', 'code': '200', 'data': data})


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
