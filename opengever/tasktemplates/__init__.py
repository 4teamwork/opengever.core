from opengever.tasktemplates.interfaces import ITaskTemplateSettings
from plone import api
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("opengever.tasktemplates")


def is_tasktemplatefolder_nesting_allowed():
    return api.portal.get_registry_record(
        'is_tasktemplatefolder_nesting_enabled',
        interface=ITaskTemplateSettings)
