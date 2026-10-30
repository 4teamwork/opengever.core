from opengever.activity.notification_email import get_notification_email
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.sources import WorkspaceContentMemberUsersSource
from opengever.ogds.models.service import ogds_service
from opengever.workspace.content_sharing_mailer import ContentSharingMailer
from opengever.workspace.utils import is_within_workspace
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import alsoProvides


class ShareContentPost(Service):

    def get_email_adresses(self, actors, is_term=False, primary_emails=None):
        emails = set()

        if is_term:
            def getToken(actor):
                return actor.token
        else:
            def getToken(actor):
                return actor['token']

        for actor in actors:
            for representative in ActorLookup(getToken(actor)).lookup().representatives():
                if representative.active:
                    if primary_emails is not None and representative.email:
                        primary_emails.add(representative.email)
                    address = get_notification_email(representative)
                    if address:
                        emails.add(address)
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
            primary_emails_to = ""
            emails_to = ""
            emails_cc = ""
            emails_bcc = self.get_email_adresses(source.search(''), self.notify_all)
        else:
            primary_emails = set()
            emails_to = self.get_email_adresses(
                self.actors_to, primary_emails=primary_emails)
            primary_emails_to = ', '.join(primary_emails)
            emails_cc = self.get_email_adresses(self.actors_cc)
            emails_bcc = ""

        sender_id = api.user.get_current().getId()
        mailer = ContentSharingMailer()
        sender = ogds_service().fetch_user(sender_id)
        # Routing the recipients must not change the existing sender policy.
        is_self_notification = bool(sender and sender.email == primary_emails_to)
        mailer.share_content(
            self.context, sender_id, emails_to, emails_cc, emails_bcc,
            self.comment, is_self_notification=is_self_notification)

        self.request.response.setStatus(204)
        return super(ShareContentPost, self).reply()
