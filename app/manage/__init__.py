# 定义管理相关的路由
from flask import Blueprint

manage = Blueprint('manage', __name__)

from app.manage import views
