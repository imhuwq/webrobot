from celery import Celery

from server.instance import celery_config

celery_app = Celery()

celery_app.config_from_object(celery_config)

from server.modules.celery.task import *
