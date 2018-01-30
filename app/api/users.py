from flask import jsonify

from app.api import api
from app.models import User


@api.route('/users/<int:user_id>')
def get_user_info(user_id):
    """
    根据id返回用户信息
    """
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_json())
