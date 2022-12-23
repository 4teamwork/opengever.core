from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IDeleter
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.dossier.dossiertemplate import is_create_dossier_from_template_available
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.repositoryroot import IRepositoryRoot
from plone import api
from zope.component import adapter


@adapter(IRepositoryRoot, IOpengeverBaseLayer)
class RepositoryRootContextActions(BaseContextActions):

    def is_download_excel_available(self):
        return api.user.has_permission('opengever.repository: Export repository', obj=self.context)

    def is_prefix_manager_available(self):
        return api.user.has_permission('opengever.repository: Unlock Reference Prefix',
                                       obj=self.context)


@adapter(IRepositoryFolder, IOpengeverBaseLayer)
class RepositoryFolderContextActions(BaseContextActions):

    def is_delete_repository_available(self):
        return IDeleter(self.context).is_delete_allowed()

    def is_dossier_with_template_available(self):
        return is_create_dossier_from_template_available(self.context)

    def is_prefix_manager_available(self):
        return api.user.has_permission('opengever.repository: Unlock Reference Prefix',
                                       obj=self.context)
