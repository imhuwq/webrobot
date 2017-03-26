from server.resources.api_v1 import apiv1, BaseHandler

from server.models.celery import TaskRole
from server.models.celery import PeriodicTask as Task

from server.modules.celery.task.tasks import TaskTypes

from server.application.tornado_handler import login_required, Argument

task = apiv1.create_resource('task', prefix='/tasks')


# get task info or create task
@task.route('/')
class TaskIndexResource(BaseHandler):
    @login_required
    def get(self):
        tasks = self.query(Task).filter_by(_role=TaskRole.INITIALIZER.value).all()
        task_count = len(tasks)
        task_types = [value.value for value in TaskTypes.__members__.values()]
        self.start_response(task_count=task_count, task_types=task_types)

    @login_required
    def post(self):
        type_, args, kwargs = self.parse_arguments([Argument('type', type_=str),
                                                    Argument('args', type_=list),
                                                    Argument('kwargs', type_=dict)])
