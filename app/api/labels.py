from app.api import api
from app.api.responses import response
from app.models import Label


@api.route('/labels/')
def get_labels():
    """
    请求文章分类标签
    """
    labels = Label.query.all()
    data = {'labels': [label.to_json() for label in labels]}
    return response(data)
