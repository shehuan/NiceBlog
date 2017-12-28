from flask import Blueprint

# 两个参数分别指定蓝本的名字、蓝本所在的包或模块
main = Blueprint('main', __name__)

# 导入路由模块、错误处理模块，将其和蓝本关联起来
# 在蓝本的末尾导入在两个模块里还要导入蓝本，防止循环导入依赖
from app.main import views, errors
