from flask import request, current_app

from app.api import api
from app.api.responses import response
from app.decorators import permission_required
from app.models import Favourite, User, Permission


@api.route('/users/<int:user_id>/favourites')
def get_favourites(user_id):
    """
     分页请求对应id的用户喜欢的文章
    """
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(user_id)
    pagination = user.favourites.order_by(Favourite.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    favourites = pagination.items
    data = {
        'favourites': [favourite.to_json() for favourite in favourites],
        'current_page': page,
        'total_page': pagination.total
    }
    return response(data)


@api.route('/blogs/<int:blog_id>/favourite')
@permission_required(Permission.FAVOURITE)
def favourite_blog(blog_id):
    """
    喜欢某篇文章
    """
    pass


@api.route('/blogs/<int:blog_id>/unfavourite')
def cancel_favourite_blog(blog_id):
    """
    取消喜欢某篇文章
    """
    pass
