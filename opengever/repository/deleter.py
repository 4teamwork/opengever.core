from opengever.repository.interfaces import IDuringRepositoryDeletion
from plone import api
from zExceptions import Unauthorized
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class RepositoryDeleter(object):

    def __init__(self, repository):
        self.repository = repository

    def delete(self):
        if not self.is_deletion_allowed():
            raise Unauthorized

        # add request layer to allow deletion of the repository
        request = getRequest()
        alsoProvides(request, IDuringRepositoryDeletion)

        api.content.delete(obj=self.repository)

        noLongerProvides(request, IDuringRepositoryDeletion)

    def is_deletion_allowed(self):
        return self.is_repository_empty()

    def is_repository_empty(self):
        return self.repository.objectCount() == 0
