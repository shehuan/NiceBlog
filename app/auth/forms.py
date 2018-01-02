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
                                                  EqualTo('password', '两次输入的密码不一致')])
    submit = SubmitField("注册")

    # validate_字段名 的方法和常规的验证函数一起被调用
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('昵称已存在')


class ChangePasswordForm(FlaskForm):
    """
    修改密码表单
    """
    old_password = PasswordField('原始密码', validators=[DataRequired(), Length(6, 16, message='密码长度为6到16位')])
    new_password = PasswordField('新密码', validators=[DataRequired(), Length(6, 16, message='密码长度为6到16位')])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired(), Length(6, 16, message='密码长度为6到16位'),
                                                       EqualTo('new_password', '两次输入的新密码不一致')])
    submit = SubmitField("修改密码")


class ResetPasswordRequestForm(FlaskForm):
    """
    重置密码：填写邮箱表单
    """
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email(message='邮箱格式错误')])
    submit = SubmitField("确定")


class ResetPasswordForm(FlaskForm):
    """
    重置密码：设置新密码表单
    """
    password = PasswordField('新密码', validators=[DataRequired(), Length(6, 16, message='密码长度为6到16位')])
    password2 = PasswordField('确认新密码', validators=[DataRequired(), Length(6, 16, message='密码长度为6到16位'),
                                                   EqualTo('password', '两次输入的密码不一致')])
    submit = SubmitField('确定')
