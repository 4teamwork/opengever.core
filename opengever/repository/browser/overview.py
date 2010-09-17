from five import grok
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.repository.interfaces import IRepositoryFolder


class RepositoryOverview(grok.View, OpengeverTab):

    grok.context(IRepositoryFolder)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def catalog(self, types):
        return self.context.portal_catalog(
            portal_type=types,
            path=dict(
                depth=1,
                query='/'.join(self.context.getPhysicalPath())),
            sort_on='modified',
            sort_order='reverse')

    def boxes(self):
        items = [
            dict(id = 'repostories', content=self.repostories()),
            dict(id = 'dossiers', content=self.dossiers()),
            ]
        return items

    def repostories(self):
        return self.catalog(['opengever.repository.repositoryfolder', ])[:5]

    def dossiers(self):
        return self.catalog([
            'opengever.dossier.projectdossier',
            'opengever.dossier.businesscasedossier', ])[:5]
