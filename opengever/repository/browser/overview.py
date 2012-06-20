from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.tabbedview.browser.tabs import OpengeverTab


class RepositoryRootOverview(grok.View, OpengeverTab):

    grok.context(IRepositoryRoot)
    grok.name('tabbedview_view-overview')
    grok.require('zope2.View')

    show_searchform = False

    @property
    def catalog(self):
        try:
            return self._catalog
        except AttributeError:
            self._catalog = getToolByName(self.context, 'portal_catalog')
            return self._catalog

    def get_amount_of_dossiers(self):
        """Returns the amount of dossiers recursively in this context.
           Do not count subdossiers.

        """
        return len(
            self.catalog(
                object_provides=[
                    'opengever.dossier.behaviors.dossier.IDossierMarker'],
                path='/'.join(self.context.getPhysicalPath()),
                is_subdossier=False))

    def get_amount_of_tasks(self):
        """Returns the amount of tasks recursivley in this context.
        """
        return len(self.catalog(
                object_provides=['opengever.task.task.ITask'],
                path='/'.join(self.context.getPhysicalPath())))

    def get_amount_of_documents(self):
        """Returns the amount of documents recursively in this context.
        """
        return len(self.catalog(
                object_provides=[
                    'opengever.document.document.IDocumentSchema',
                    'ftw.mail.mail.IMail'],
                path='/'.join(self.context.getPhysicalPath())))
