from opengever.base.interfaces import IDeleter
from plone.restapi.services.content.delete import ContentDelete
from zope.component import getAdapter


class GeverContentDelete(ContentDelete):
    """Deletes an object through a deleter-adapter. The adapter
    takes care of permission checks and further validation steps.
    """
    def reply(self):
        deleter = getAdapter(self.context, IDeleter)
        deleter.delete()
        return self.reply_no_content()
