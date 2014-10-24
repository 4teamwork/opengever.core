from opengever.globalindex.model.task import Task


def indexed_task_link_helper(item, value):
    """Tabbedview helper wich call the task link generation without the workflow
    state icon and the repsonsible info.
    """
    return item.get_link(with_state_icon=False, with_responsible_info=False)


def get_selected_items(context, request):
    """Returns a set of SQLAlchemy objects, for "task_id:list given
    in the request"
    """
    ids = request.get('task_ids', [])
    if ids:
        tasks = Task.query.by_ids(ids)
        keys = ids
        attr = 'task_id'

    else:
        # empty generator
        return

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
