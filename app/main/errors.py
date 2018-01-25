from flask import render_template

from . import main


# 使用errorhandler装饰器，只有蓝本才能触发处理程序
# 要想触发全局的错误处理程序，要用app_errorhandler
@main.app_errorhandler(403)
def forbidden(e):
    return render_template('error/403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500
