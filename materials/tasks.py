import logging
from config.celery import app
from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task
def example_task():
    logger.info("Пример периодической задачи выполнен")
    return "Задача выполнена успешно"


@app.task
def my_periodic_task():
    return print("Выполнение периодической задачи")
