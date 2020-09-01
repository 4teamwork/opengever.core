from opengever.ogds.base.utils import ogds_service
from opengever.workspace.content_sharing_mailer import ContentSharingMailer
from opengever.workspace.utils import is_within_workspace
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import alsoProvides


class ShareContentPost(Service):

    def get_email_adresses(self, users):
        service = ogds_service()
        emails = []
        for user in users:
            emails.append(service.fetch_user(user['token']).email)
        return ', '.join(emails)

    def extract_data(self):
        data = json_body(self.request)
        self.comment = data.get('comment', u'')
        self.users_to = data.get('users_to', [])
        if not self.users_to:
            raise BadRequest("Property 'users_to' is required")
        self.users_cc = data.get('users_cc', [])

    def reply(self):
        if not is_within_workspace(self.context):
            raise BadRequest("'{}' is not within a workspace".format(self.context.getId()))
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        self.extract_data()
        emails_to = self.get_email_adresses(self.users_to)
        emails_cc = self.get_email_adresses(self.users_cc)

        sender_id = api.user.get_current().getId()
        mailer = ContentSharingMailer()
        mailer.share_content(self.context, sender_id, emails_to, emails_cc, self.comment)

        self.request.response.setStatus(204)
        return super(ShareContentPost, self).reply()
