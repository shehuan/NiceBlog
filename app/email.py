from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kw):
    """
    :param to: 收件人地址
    :param subject: 邮件主题
    :param template: 内容模板
    :param kw: 需要的参数
    :return:
    """
    app = current_app._get_current_object()
    msg = Message(app.config['NICEBLOG_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['NICEBLOG_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kw)
    msg.html = render_template(template + '.html', **kw)
    # 开启线程发送邮件
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
