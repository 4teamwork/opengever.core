from opengever.base.content_deleter import BaseContentDeleter
from opengever.repository.interfaces import IDuringRepositoryDeletion
from opengever.repository.interfaces import IRepositoryFolder
from zExceptions import Forbidden
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


@adapter(IRepositoryFolder)
class RepositoryDeleter(BaseContentDeleter):

    def delete(self):
        self.verify_may_delete()

        # add request layer to allow deletion of the repository
        request = getRequest()
        alsoProvides(request, IDuringRepositoryDeletion)

        self._delete()

        noLongerProvides(request, IDuringRepositoryDeletion)

    def verify_may_delete(self, **kwargs):
        super(RepositoryDeleter, self).verify_may_delete()
        if not self.context.objectCount() == 0:
            raise Forbidden("Repository is not empty.")
