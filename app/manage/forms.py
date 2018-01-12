from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField


class PermissionForm(FlaskForm):
    """
    登录表单
    """
    favourite = BooleanField('喜欢', default=False)
    commit = BooleanField('评论', default=True)
    save = SubmitField('确定')
