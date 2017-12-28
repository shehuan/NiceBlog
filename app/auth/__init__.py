# 定义用户认证相关的路由
from flask import Blueprint

auth = Blueprint('auth', __name__)

from app.auth import views
