from opengever.api.task import TaskDeserializeFromJson
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IDeserializeFromJson)
@adapter(ITaskTemplate, Interface)
class TaskTemplateDeserializeFromJson(TaskDeserializeFromJson):
    """A tasktemplate specific deserializer which allows to pass in the
    responsible_client and responsible value in a combined string.
    In the same way as it is exposed by the API's querysoure endpoint.
    """
