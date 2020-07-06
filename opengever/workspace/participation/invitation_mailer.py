from opengever.activity.mailer import Mailer
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.workspace.participation import serialize_and_sign_payload
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.workspace")


class InvitationMailer(Mailer):

    template = ViewPageTemplateFile("templates/invitation_mail.pt")
    default_addr_header = u'Teamraum'

    def send_invitation(self, invitation):
        target_workspace = uuidToObject(invitation['target_uuid'])

        subject = translate(
            _(u'invitation_mail_subject',
              default=u'Invitation to workspace "${title}"',
              mapping={'title': target_workspace.title}),
            context=self.request
        )

        payload = serialize_and_sign_payload({'iid': invitation['iid']})
        accept_url = "{}/@@my-invitations/accept?invitation={}".format(
            target_workspace.absolute_url(), payload)

        inviter = ActorLookup(invitation['inviter']).lookup()

        title = translate(
            _(
                u'invitation_mail_description',
                default=u'You were invited by ${user} to the workspace "${title}".',
                mapping={'title': target_workspace.title,
                         'user': inviter.get_label()}
            ),
            context=self.request
        )
        content = translate(
            _(
                u'invitation_mail_summary',
                default=u'Hello,\n'
                        u'\n'
                        u'You were invited by ${user} to the workspace "${title}" at ${platform}.\n'
                        u'\n'
                        u'Please click the following link if you want to accept the invitation:\n'
                        u'${accept_url}',
                mapping={'title': target_workspace.title,
                         'user': inviter.get_label(with_principal=False),
                         'platform': get_current_admin_unit().public_url,
                         'accept_url': accept_url}
            ),
            context=self.request
        )
        comment_title = translate(
            _(
                u'invitation_mail_message_title',
                default=u'Message from ${user}:',
                mapping={'user': inviter.get_label(with_principal=False)}
            ),
            context=self.request
        )

        data = {
            'title': title,
            'content': content.splitlines(),
            'comment_title': comment_title,
            'comment': invitation['comment'].splitlines(),
            'public_url': get_current_admin_unit().public_url,
        }
        msg = self.prepare_mail(subject=subject, to_email=invitation['recipient_email'],
                                from_userid=invitation['inviter'], data=data)

        self.send_mail(msg)
