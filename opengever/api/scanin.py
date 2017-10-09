from opengever.base.command import CreateDocumentCommand
from plone import api
from plone.restapi.services import Service
from plone.restapi.services.content.utils import create
from plone.restapi.services.content.utils import rename
from zope.interface import alsoProvides
import plone.protect.interfaces


class ScanIn(Service):
    """Endpoint for uploading documents from a scanner"""

    def reply(self):

        userid = self.request.form.get('userid')
        if not userid:
            return self.error(message='Missing userid.')

        file_ = self.request.form.get('file')
        if not file_:
            return self.error(message='Missing file.')

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        try:
            adopt_user = api.env.adopt_user(username=userid)
        except api.exc.UserNotFoundError:
            return self.error(message='Unknown user.')

        with adopt_user:
            destination = self.destination()
            if destination is None:
                return self.error(message='Destination does not exist.')
            filename = file_.filename.decode('utf8')
            command = CreateDocumentCommand(destination, filename, file_)
            command.execute()

        self.request.response.setStatus(201)
        return super(ScanIn, self).reply()

    def destination(self):
        """Return the destination for scanned documents."""
        portal = api.portal.get()
        destination = self.request.form.get('destination', 'inbox')
        org_unit = self.request.form.get('org_unit')

        if destination == 'inbox':
            # Find inbox for the given org_unit
            inbox_container = portal.listFolderContents(
                contentFilter={'portal_type': 'opengever.inbox.container'})
            if inbox_container:
                inboxes = inbox_container[0].listFolderContents(
                    contentFilter={'portal_type': 'opengever.inbox.inbox'})
                for inbox in inboxes:
                    inbox_ou = inbox.get_responsible_org_unit()
                    if (inbox_ou.unit_id == org_unit or
                            inbox_ou.title == org_unit):
                        return inbox
            else:
                inboxes = portal.listFolderContents(
                    contentFilter={'portal_type': 'opengever.inbox.inbox'})
                if inboxes:
                    return inboxes[0]

        elif destination == 'private':
            # Try to find a dossier with title 'Scaneingang'
            mtool = api.portal.get_tool(name='portal_membership')
            private_folder = mtool.getHomeFolder()
            if private_folder is None:
                return
            catalog = api.portal.get_tool(name='portal_catalog')
            dossiers = catalog(
                portal_type='opengever.private.dossier',
                path={'query': '/'.join(private_folder.getPhysicalPath()),
                      'depth': -1},
                sortable_title='scaneingang',  # Exact match
            )
            if dossiers:
                return dossiers[0].getObject()

            # No dossier found, create a new one
            obj = create(
                private_folder,
                'opengever.private.dossier',
                title='Scaneingang')
            rename(obj)
            return obj

    def error(self, status=400, type_='BadRequest', message=''):
        self.request.response.setStatus(status)
        return {'error': {
            'type': type_,
            'message': message,
        }}
