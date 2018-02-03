from flask import render_template, request, jsonify

from . import main


# 使用errorhandler装饰器，只有蓝本才能触发处理程序
# 要想触发全局的错误处理程序，要用app_errorhandler
@main.app_errorhandler(403)
def forbidden(e):
    if request.url.find('api') != -1:
        return jsonify({'error': '无访问权限', 'code': '403', 'data': ''})
    return render_template('error/403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    if request.url.find('api') != -1:
        return jsonify({'error': '请求的资源不存在', 'code': '404', 'data': ''})
    return render_template('error/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.url.find('api') != -1:
        return jsonify({'error': '服务器内部错误', 'code': '500', 'data': ''})
    return render_template('error/500.html'), 500
