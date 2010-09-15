from five import grok
from opengever.dossier.browser.overview import DossierOverview
from opengever.inbox.inbox import IInbox


class InboxOverview(DossierOverview):
    grok.context(IInbox)
    grok.name('tabbedview_view-overview')

    def boxes(self):

        #TODO: implements the sharing box n ot work yet
        # dict(id = 'sharing', content=self.sharing())],
        items = [[dict(id = 'tasks', content=self.tasks()),
                  dict(id = 'journal', content=self.journal()), ],
                 [dict(id = 'documents', content=self.documents()), ]]
        return items
