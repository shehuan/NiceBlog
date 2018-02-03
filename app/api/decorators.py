from functools import wraps

from flask import g

from app.api.responses import forbidden
from app.models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('没有操作权限')
            return f(*args, **kwargs)

        return wrapper

    return decorator


def comment_required(f):
    return permission_required(Permission.COMMENT)(f)


def favourite_required(f):
    return permission_required(Permission.FAVOURITE)(f)
