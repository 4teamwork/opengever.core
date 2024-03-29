from zope import schema
from zope.interface import Interface


class IFromTasktemplateGenerated(Interface):
    """Marker Interfaces for Task who are autmaticly generated by
    release a tasktemplate"""


class IFromSequentialTasktemplate(IFromTasktemplateGenerated):
    """Deprecated and no longer used marker interfaces."""


class IFromParallelTasktemplate(IFromTasktemplateGenerated):
    """Deprecated and no longer used marker interfaces."""


class IPartOfSequentialProcess(IFromTasktemplateGenerated):
    """"Marker interfaces for a task which are part o a sequential
    process/subprocess."""


class IPartOfParallelProcess(IFromTasktemplateGenerated):
    """"Marker interfaces for a task which are part o a parallel
    process/subprocess."""


class IContainProcess(IFromTasktemplateGenerated):
    """Marker interface for task which contains a process.
    """


class IContainSequentialProcess(IContainProcess):
    """"Marker interfaces for a task which contains a sequential
    process/subprocess."""


class IContainParallelProcess(IContainProcess):
    """"Marker interfaces for a task which contains a parallel
    process/subprocess."""


class IDuringTaskTemplateFolderTriggering(Interface):
    """Request marker present while generating tasks from a task template folder.
    """


class IDuringTaskTemplateFolderWorkflowTransition(Interface):
    """Request marker present during workflow transitions of TaskTemplateFolders.
    """


class ITaskTemplateSettings(Interface):

    is_tasktemplatefolder_nesting_enabled = schema.Bool(
        title=u'Enable nesting of tasktemplatefolders',
        description=u'Allow nesting of tasktemplatefolders.',
        default=False)
