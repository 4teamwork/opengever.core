from plone import api
from zExceptions import Unauthorized


class RepositoryDeleter(object):

    def __init__(self, repository):
        self.repository = repository

    def delete(self):
        if not self.is_deletion_allowed():
            raise Unauthorized

        api.content.delete(obj=self.repository)

    def is_deletion_allowed(self):
        return self.is_repository_empty()

    def is_repository_empty(self):
        return len(self.repository.listFolderContents()) == 0
