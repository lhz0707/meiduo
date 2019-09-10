from celery_tasks.main import celery_app
from celery_tasks.yuntongxun.sms import CCP


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile,sms_code):
    ccp=CCP()
    ccp.send_template_sms(mobile, [sms_code, '5'], 1)