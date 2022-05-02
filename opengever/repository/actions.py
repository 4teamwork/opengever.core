from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
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
