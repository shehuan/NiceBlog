from functools import wraps

from flask_login import current_user
from flask import abort

from app.models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def comment_required(f):
    return permission_required(Permission.COMMENT)(f)


def favourite_required(f):
    return permission_required(Permission.FAVOURITE)(f)
