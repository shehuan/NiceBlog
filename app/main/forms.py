from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class BlogForm(FlaskForm):
    """创建/编辑博客表单"""
    title = StringField('标题', validators=[DataRequired(), Length(1, 128)])
    content = PageDownField('文章内容', validators=[DataRequired()])
    submit = SubmitField('发布')
    save = SubmitField('保存')
