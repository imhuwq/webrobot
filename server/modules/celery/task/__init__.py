from server.modules.celery import celery_app
from server.modules.celery.task.requests_task import RequestsTask


@celery_app.task(name='http_request.requests.get')
def requests_get(url, headers=None, cookies=None, params=None, data=None):
    task_instance = RequestsTask('get', url, headers=headers, cookies=cookies, params=params, data=data)
    print(url)
    # result = task_instance.start()
    # with open('te.html', 'w') as f:
    #     f.write(result.text)
