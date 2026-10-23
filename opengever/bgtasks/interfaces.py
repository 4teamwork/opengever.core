from zope import schema
from zope.interface import Interface


class IBackgroundTaskSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable background tasks',
        description=u'Whether background tasks are queued and executed '
                    u'asynchronously by the worker. When disabled, '
                    u'queue_task() executes tasks synchronously instead.',
        default=True)
