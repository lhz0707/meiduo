# 实现验证邮箱异步任务
from django.core.mail import  send_mail
from celery_tasks.main import celery_app
@celery_app.task(name='send_emails')
def send_emails(to_email,verify_url,email_from):

    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    send_mail(subject, '', email_from, [to_email], html_message=html_message)
