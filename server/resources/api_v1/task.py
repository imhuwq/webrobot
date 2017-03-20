from server.resources.api_v1 import apiv1, BaseHandler

from server.models.celery import PeriodicTask as Task
from server.models.celery import TaskRole

task = apiv1.create_resource('task', prefix='/tasks')


# test task api is accessible
@task.route('/')
class TaskIndexResource(BaseHandler):
    def get(self):
        tasks = self.query(Task).filter_by(_role=TaskRole.INITIALIZER.value).all()
        task_count = len(tasks)
        self.start_response(task_count=task_count)
