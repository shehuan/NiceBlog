from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class BlogForm(FlaskForm):
    """
    创建/编辑博客表单
    """
    title = StringField('文章标题', validators=[DataRequired(), Length(1, 128)])
    labels = StringField('文章标签', validators=[DataRequired()])
    summary = TextAreaField('文章概要', validators=[DataRequired()])
    content = PageDownField('文章内容', validators=[DataRequired()])
    publish = SubmitField('发布')
    save = SubmitField('保存')


class CommentForm(FlaskForm):
    """
    创建评论的表单
    """
    content = TextAreaField('写下你的评论...')
    submit = SubmitField('发送')
