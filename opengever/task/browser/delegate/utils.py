from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.dexterity.utils import iterSchemata
from z3c.relationfield import RelationValue
from zope import schema
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
import urllib


def encode_data(data):
    """Encode a data dict so that it can be passed in a GET request.
    """

    prepared_data = []

    for key, value in data.items():
        if hasattr(value, '__iter__'):
            for val in value:
                prepared_data.append(('%s:list' % key, val))

        else:
            prepared_data.append((key, value))

    return urllib.urlencode(prepared_data)


def create_subtasks(task, responsibles, documents, data):
    subtasks = []

    for responsible in responsibles:
        subtask_data = data.copy()

        # responsible client & user
        client, user = responsible.split(':', 1)
        subtask_data['responsible_client'] = client
        subtask_data['responsible'] = user

        # remove predecessor
        subtask_data['predecessor'] = None

        # related documents
        subtask_data['relatedItems'] = []

        for intid in documents:
            subtask_data['relatedItems'].append(RelationValue(int(intid)))

        subtasks.append(create_subtask(task, subtask_data))

    return subtasks


def create_subtask(task, data):
    subtask = createContent('opengever.task.task',
                            id=data['title'],
                            **data)
    notify(ObjectCreatedEvent(subtask))
    subtask = addContentToContainer(task, subtask,
                                    checkConstraints=True)

    for schemata in iterSchemata(subtask):
        super_repr = schemata(task)
        repr = schemata(subtask)

        for name, field in schema.getFieldsInOrder(schemata):
            if name in data:
                value = data[name]

            else:
                value = getattr(super_repr, name, None)

            setattr(repr, name, value)

    return notify(ObjectModifiedEvent(subtask))
