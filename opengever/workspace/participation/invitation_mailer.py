from opengever.activity.mailer import Mailer
from opengever.ogds.base.actor import ActorLookup
from opengever.workspace.participation import serialize_and_sign_payload
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("opengever.workspace")


class InvitationMailer(Mailer):

    template = ViewPageTemplateFile("templates/invitation_mail.pt")

    def send_invitation(self, invitation):
        target_workspace = uuidToObject(invitation['target_uuid'])

        data = {}
        subject = translate(
            _(u'invitation_mail_subject',
              default=u'Invitation to workspace "${title}"',
              mapping={'title': target_workspace.title}),
            context=self.request
            )

        payload = serialize_and_sign_payload({'iid': invitation['iid']})
        accept_link = "{}/@@my-invitations/accept?invitation={}".format(
            target_workspace.absolute_url(), payload)

        inviter = ActorLookup(invitation['inviter']).lookup()

        title = translate(
            _(u'invitation_mail_description',
              default=u'You were invited by ${user} to the workspace "${title}".',
              mapping={'title': target_workspace.title,
                       'user': inviter.get_label()}),
            context=self.request
            )
        accept = translate(
            _(u'invitation_accept',
              default=u'Accept: ${accept_link}',
              mapping={'accept_link': accept_link})
            )
        data['title'] = title
        data['description'] = invitation['comment']
        data['accept'] = accept
        msg = self.prepare_mail(subject=subject, to_email=invitation['recipient_email'],
                                from_userid=invitation['inviter'], data=data)

        self.send_mail(msg)
