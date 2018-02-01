from flask import render_template, request, jsonify

from . import main


# 使用errorhandler装饰器，只有蓝本才能触发处理程序
# 要想触发全局的错误处理程序，要用app_errorhandler
@main.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden', 'code': '403', 'data': ''})
        return response
    return render_template('error/403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found', 'code': '404', 'data': ''})
        return response
    return render_template('error/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error', 'code': '500', 'data': ''})
        return response
    return render_template('error/500.html'), 500
