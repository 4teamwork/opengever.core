from opengever.globalindex.model.task import Task
from plone import api
from sqlalchemy.sql.expression import desc


def indexed_task_link_helper(item, value):
    """Tabbedview helper wich call the task link generation without the workflow
    state icon and the repsonsible info.
    """
    return item.get_link(with_state_icon=False, with_responsible_info=False)


def get_selected_items(context, request):
    """Returns a set of SQLAlchemy objects, for "task_id:list" or "tasks:list"
    given in the request"
    """
    ids = request.get('task_ids', [])  # a list of `task_id`s within the ogds
    tasks = request.get('tasks', [])  # a list of `@id`s of tasks
    include_subtasks = request.get('include_subtasks', '').lower() == 'true'

    if ids:
        tasks = Task.query.by_ids(ids)
        keys = ids
        attr = 'task_id'

    elif tasks:
        portal_url = api.portal.get().absolute_url()
        paths = [task.replace(portal_url, '').lstrip('/') for task in tasks]
        tasks = Task.query.by_paths(paths)
        keys = paths
        attr = 'physical_path'

    else:
        # empty generator
        return

    if include_subtasks:
        all_subtasks = []
        for task in tasks:
            subtasks = Task.query.subtasks_by_task(task).order_by(
                desc(Task.physical_path)).all()
            all_subtasks.extend(subtasks)
            key_index = keys.index(getattr(task, attr)) + 1
            for subtask in subtasks:
                keys.insert(key_index, getattr(subtask, attr))
        tasks.extend(all_subtasks)

    # we need to sort the result by our ids list, because the
    # sql query result is not sorted...
    # create a mapping:
    mapping = {}
    for task in tasks:
        mapping[str(getattr(task, attr))] = task

    # get the task from the mapping
    for taskid in keys:
        task = mapping.get(str(taskid))
        if task:
            yield task
