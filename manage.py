# 启动程序
import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.models import User, Role, Permission, Blog, Comment, Favourite, Label

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


# 注册程序、数据库实例、数据模型，这些对象可直接导入shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Blog=Blog, Comment=Comment, Favourite=Favourite, Label=Label,
                Permission=Permission)


# 集成自定义shell命令
# python manage.py {shell, db, test, runserver}
manager.add_command('shell', Shell(make_context=make_shell_context))

# 集成数据库迁移命令，步骤1执行一次即可，需要修改数据模型后需要迁移执行2、3步骤即可
# 1.创建迁移仓库：python manage.py db init
# 2.创建迁移脚本：python manage.py db migrate --message "initial migration"
# 3.更新数据库：python manage.py db upgrade
manager.add_command('db', MigrateCommand)


# 自定义单元测试命令
# 命令名：test
# 执行方式：python manage.py test
@manager.command
def test():
    import unittest
    # 查找测试文件的文件夹
    tests = unittest.TestLoader().discover('tests')
    # 执行测试
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
