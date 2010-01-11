from five import grok
from Products.statusmessages.interfaces import IStatusMessage
from Acquisition import aq_inner, aq_parent

from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
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

        # all documents are in subdossier
        docs = self.context.portal_catalog(
                                        portal_type="opengever.document.document",
                                        path=dict(depth=1,
                                                  query='/'.join(self.context.getPhysicalPath()),
                                                  ),
                                                  sort_on='modified',
                                                  sort_order='reverse')
        # there are subdossiers
        subdossiers = self.context.portal_catalog(
                                            portal_type="opengever.dossier.businesscasedossier",
                                            path=dict(depth=1,
                                                      query='/'.join(self.context.getPhysicalPath()),
                                                      ),
                                            is_subdossier=True,
                                                 )
        if docs.__len__() > 0:
            if subdossiers.__len__() > 0:
                errors = True
                status.addStatusMessage(_("not all documents are stored in a subdossier"), type="error")

        # all document are checked in
        docs = self.context.portal_catalog(
                                portal_type="opengever.document.document",
                                path=dict(depth=2,
                                    query='/'.join(self.context.getPhysicalPath()),
                                ),
                                review_state = 'checked_out',
                                sort_on='modified',
                                sort_order='reverse')

        if docs.__len__() > 0:
            errors = True
            status.addStatusMessage(_("not all documents are checked in"), type="error")

        #all tasks are closed
        tasks_closed = self.context.portal_catalog(
                                portal_type="ftw.task.task",
                                path=dict(depth=2,
                                    query='/'.join(self.context.getPhysicalPath()),
                                ),
                                review_state = ('task-state-resolved', 'task-state-cancelled', 'task-state-rejected'),
        )

        tasks = self.context.portal_catalog(
                                portal_type="ftw.task.task",
                                path=dict(depth=2,
                                    query='/'.join(self.context.getPhysicalPath()),
                                ),
        )

        if tasks_closed.__len__() != tasks.__len__():
            errors = True
            status.addStatusMessage(_("not all task are closed"), type="error")

        # an end-date are entered
        if not IDossier(self.context).end:
            errors = True
            status.addStatusMessage(_("no end date are entered"), type="error")

        if errors:
            self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + '/transition-archive')
