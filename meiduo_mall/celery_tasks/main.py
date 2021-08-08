from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

celery_app = Celery('celery_tasks')

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')

# 自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])