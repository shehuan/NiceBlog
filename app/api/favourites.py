from flask import request, current_app, g

from app import db
from app.api import api
from app.api.decorators import favourite_required
from app.api.responses import response
from app.models import Favourite, User, Blog


@api.route('/users/<int:user_id>/favourites/')
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


@api.route('/blogs/<int:blog_id>/favourite/', methods=['POST'])
@favourite_required
def favourite_blog(blog_id):
    """
    喜欢某篇文章
    """
    blog = Blog.query.get_or_404(blog_id)
    favourite = Favourite(user=g.current_user, blog=blog)
    db.session.add(favourite)
    db.session.commit()
    return response()


@api.route('/blogs/<int:blog_id>/unfavourite/', methods=['POST'])
def cancel_favourite_blog(blog_id):
    """
    取消喜欢某篇文章
    """
    favourite = Favourite.query.filter_by(blog_id=blog_id).first_or_404()
    db.session.delete(favourite)
    db.session.commit()
    return response()
