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

    def get_email_adresses(self, actors):
        service = ogds_service()
        for actor in actors:
            emails.append(service.fetch_user(actor['token']).email)
        return ', '.join(emails)

    def extract_data(self):
        data = json_body(self.request)
        self.comment = data.get('comment', u'')
        self.actors_to = data.get('actors_to', [])
        if not self.actors_to:
            raise BadRequest("Property 'actors_to' is required")
        self.actors_cc = data.get('actors_cc', [])

    def reply(self):
        if not is_within_workspace(self.context):
            raise BadRequest("'{}' is not within a workspace".format(self.context.getId()))
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        self.extract_data()
        emails_to = self.get_email_adresses(self.actors_to)
        emails_cc = self.get_email_adresses(self.actors_cc)

        sender_id = api.user.get_current().getId()
        mailer = ContentSharingMailer()
        mailer.share_content(self.context, sender_id, emails_to, emails_cc, self.comment)

        self.request.response.setStatus(204)
        return super(ShareContentPost, self).reply()
