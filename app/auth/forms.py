from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    """
    登录表单
    """
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email(message='邮箱格式错误')])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 16, message='密码长度为6到16位')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    """
    注册表单
    """
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email(message='邮箱格式错误')])
    username = StringField('昵称', validators=[DataRequired(), Length(3, 10, message='昵称长度为3到10位'),
                                             Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, '昵称必须以字母开头，包含字母、数字、下划线')])
    password = PasswordField('输入密码', validators=[DataRequired(), Length(6, 16, message='密码长度为6到16位')])
    password2 = PasswordField('确认密码', validators=[DataRequired(), Length(6, 16, message='密码长度为6到16位'),
                                                  EqualTo('password', "两次输入的密码不一致")])
    submit = SubmitField("注册")

    # validate_字段名 的方法和常规的验证函数一起被调用
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('昵称已存在')
