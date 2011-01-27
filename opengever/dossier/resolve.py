from five import grok
from Products.statusmessages.interfaces import IStatusMessage
from Acquisition import aq_inner, aq_parent

from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier import _


class resolve(grok.CodeView):
    grok.context(IDossierMarker)
    grok.name('transition-resolve')
    grok.require('zope2.View')

    def render(self):
        parent = aq_parent(aq_inner(self.context))
        if IDossierMarker.providedBy(parent):
            self.request.RESPONSE.redirect(self.context.absolute_url() + '/content_status_modify?workflow_action=dossier-transition-resolve')

        errors = False
        status = IStatusMessage(self.request)

        if not self.is_all_supplied():
            errors = True
            status.addStatusMessage(_("not all documents and tasks are stored in a subdossier"), type="error")

        if not self.is_all_checked_in():
            errors = True
            status.addStatusMessage(_("not all documents are checked in"), type="error")

        if not self.is_all_closed():
            errors = True
            status.addStatusMessage(_("not all task are closed"), type="error")

        if errors:
            self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + '/transition-archive')

    def is_all_supplied(self):
        """Check if all tasks and all documents are supplied in a subdossier
           provided there are any subdossiers

        """
        subddosiers = self.context.getFolderContents(
            {'object_provides':
                'opengever.dossier.behaviors.dossier.IDossierMarker',}
        )

        if len(subddosiers) > 0:
            results = self.context.getFolderContents({
                'portal_type':['opengever.task.task',
                    'opengever.document.document']
                }
            )

            if len(results) > 0:
                return False

        return True

    def is_all_closed(self):
        """ Check if all tasks are in a closed state.

        closed: - cancelled
                - rejected
                - tested and closed

        """

        tasks_closed = self.context.portal_catalog(
            portal_type="opengever.task.task",
            path=dict(query='/'.join(self.context.getPhysicalPath()),
            ),
            review_state = ('task-state-cancelled',
                'task-state-rejected', 'task-state-tested-and-closed'),
        )

        tasks = self.context.portal_catalog(
            portal_type="opengever.task.task",
            path=dict(depth=2,
                query='/'.join(self.context.getPhysicalPath()),
            ),
        )

        if len(tasks_closed) < len(tasks):
            return False
        else:
            return True

    def is_all_checked_in(self):
        """ check if all documents in this path are checked in """

        # all document are checked in
        docs = self.context.portal_catalog(
            portal_type="opengever.document.document",
            path=dict(depth=2,
                query='/'.join(self.context.getPhysicalPath()),
            ),
            review_state = 'document-state-checked_out',
        )

        if len(docs) == 0:
            return True
        else:
            return False
