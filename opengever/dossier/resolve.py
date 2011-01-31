from Acquisition import aq_inner, aq_parent
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.dossier import IDossier


class Resolve(grok.CodeView):

    grok.context(IDossierMarker)
    grok.name('transition-resolve')
    grok.require('zope2.View')

    def render(self):
        parent = aq_parent(aq_inner(self.context))
        errors = False
        status = IStatusMessage(self.request)

        url = self.context.absolute_url() + \
            '/content_status_modify?workflow_action=dossier-transition-resolve'

        # Check if it's a SubDossier
        if IDossierMarker.providedBy(parent):
            # If so, check for valid end date
            if not self.has_valid_enddate():
                status.addStatusMessage(
                    _("no valid end date provided"),
                    type="error") 
                return self.request.RESPONSE.redirect(self.context.absolute_url())

            # Everything ok, resolve subdossier
            self.request.RESPONSE.redirect(url)


        if not self.is_all_supplied():
            errors = True
            status.addStatusMessage(
                _("not all documents and tasks are stored in a subdossier"),
                type="error")

        if not self.is_all_checked_in():
            errors = True
            status.addStatusMessage(
                _("not all documents are checked in"),
                type="error")

        if not self.is_all_closed():
            errors = True
            status.addStatusMessage(
                _("not all task are closed"),
                type="error")



        if errors:
            self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + \
                                               '/transition-archive')

    def is_all_supplied(self):
        """Check if all tasks and all documents are supplied in a subdossier
        provided there are any subdossiers

        """
        subddosiers = self.context.getFolderContents({
                'object_provides':
                    'opengever.dossier.behaviors.dossier.IDossierMarker'})

        if len(subddosiers) > 0:
            results = self.context.getFolderContents({
                    'portal_type': ['opengever.task.task',
                                    'opengever.document.document']})

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
            path=dict(query='/'.join(self.context.getPhysicalPath())),
            review_state=('task-state-cancelled',
                          'task-state-rejected',
                          'task-state-tested-and-closed'))

        tasks = self.context.portal_catalog(
            portal_type="opengever.task.task",
            path=dict(depth=2,
                      query='/'.join(self.context.getPhysicalPath())))

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
                      query='/'.join(self.context.getPhysicalPath())))

        for doc in docs:
            if doc.checked_out:
                return False

        return True

    def has_valid_enddate(self):
        """Check if the enddate is valid.
        """
        dossier = IDossier(self.context)
        end_date = self.context.computeEndDate()

        if dossier.end is None:
            return False
        if end_date:
            if end_date < dossier.end:
                return False
        return True
