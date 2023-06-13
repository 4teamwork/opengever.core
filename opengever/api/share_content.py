from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.sources import WorkspaceContentMemberUsersSource
from opengever.workspace.content_sharing_mailer import ContentSharingMailer
from opengever.workspace.utils import is_within_workspace
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import alsoProvides


class ShareContentPost(Service):

    def get_email_adresses(self, actors, is_term=False):
        emails = set()

        if is_term:
            def getToken(actor):
                return actor.token
        else:
            def getToken(actor):
                return actor['token']

        for actor in actors:
            for representative in ActorLookup(getToken(actor)).lookup().representatives():
                if representative.active and representative.email:
                    emails.add(representative.email)
        return ', '.join(emails)

    def extract_data(self):
        data = json_body(self.request)
        self.comment = data.get('comment', u'')
        self.notify_all = data.get('notify_all', False)
        self.actors_to = data.get('actors_to', [])
        if not (self.actors_to or self.notify_all):
            raise BadRequest("Property 'notify_all' or 'actors_to' is required")
        self.actors_cc = data.get('actors_cc', [])

    def reply(self):
        if not is_within_workspace(self.context):
            raise BadRequest("'{}' is not within a workspace".format(self.context.getId()))
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        self.extract_data()

        if self.notify_all:
            source = WorkspaceContentMemberUsersSource(self.context)
            emails_to = ""
            emails_cc = ""
            emails_bcc = self.get_email_adresses(source.search(''), self.notify_all)
        else:
            emails_to = self.get_email_adresses(self.actors_to)
            emails_cc = self.get_email_adresses(self.actors_cc)
            emails_bcc = ""

        sender_id = api.user.get_current().getId()
        mailer = ContentSharingMailer()
        mailer.share_content(self.context, sender_id, emails_to, emails_cc, emails_bcc, self.comment)

        self.request.response.setStatus(204)
        return super(ShareContentPost, self).reply()
