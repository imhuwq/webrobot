from server.resources.api_v1 import apiv1, BaseHandler

from server.models.celery import TaskRole
from server.models.celery import PeriodicTask as Task

from server.modules.celery.task.tasks import TaskTypes
from server.modules.celery.task.task_validator import validate_tasks, validate_task

from server.application.tornado_handler import login_required, Argument

task = apiv1.create_resource("task", prefix="/tasks")


# get task info or create task
@task.route("/")
class TaskIndexResource(BaseHandler):
    @login_required
    def get(self):
        tasks = self.query(Task).filter_by(_role=TaskRole.INITIALIZER.value).all()
        task_count = len(tasks)
        task_types = [value.value for value in TaskTypes.__members__.values()]
        self.start_response(task_count=task_count, task_types=task_types)

    @login_required
    def post(self):
        init, chords, callback = self.parse_arguments([Argument("init", type_=dict),
                                                       Argument("chords", type_=list),
                                                       Argument("callback", type_=dict)])

        status, msg = validate_task(init)
        if status is False:
            self.raise_error(400, msg=msg)

        status, msg = validate_tasks(chords)
        if status is False:
            self.raise_error(400, msg=msg)

        status, msg = validate_task(callback)
        if status is False:
            self.raise_error(400, msg=msg)

        trigger_task = Task.new_trigger_task(self.current_user, init.get("period"))
        for chord in chords:
            Task.new_chord_task(chord, trigger_task)

        Task.new_callback_task(callback, trigger_task)
        self.db_session.commit()

        self.start_response()
