from five import grok
from opengever.document.document import IDocumentSchema
from opengever.tabbedview.browser.tabs import Tasks
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


def related_document(context):
    intids = getUtility(IIntIds)
    return intids.getId(context)


class RelatedTasks(Tasks):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-tasks')

    search_options = {'related_items': related_document}

    def update_config(self):
        Tasks.update_config(self)

        # do not search on this context, search on site
        self.filter_path = None
