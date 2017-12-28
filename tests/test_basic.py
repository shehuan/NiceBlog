import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    # 测试前执行
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        # 根据数据模型创建对应的表
        db.create_all()

    # 测试后执行
    def tearDown(self):
        db.session.remove()
        # 删除数据库中的表
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['testing'])
