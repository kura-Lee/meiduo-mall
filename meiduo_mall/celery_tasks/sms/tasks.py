from celery_tasks.main import celery_app
from libs.yuntongxun.sms import send_sms
import logging
logger = logging.getLogger('django')

@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信的异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return:
    """
    try:
        send_res = send_sms(mobile, [sms_code, 5], 1)
    except Exception as e:
        logger.error(e)
    return send_res