from opengever.activity.mailer import Mailer
from opengever.ogds.base.actor import ActorLookup
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.workspace")


class ContentSharingMailer(Mailer):

    template = ViewPageTemplateFile("content_sharing_mail.pt")
    default_addr_header = u'Teamraum'

    def share_content(self, target_object, sender_id, to_email, cc_email=None, bcc_email=None, comment=u''):

        subject = translate(
            _(u'share_mail_subject',
              default=u'Notification to "${title}"',
              mapping={'title': target_object.title}),
            context=self.request
        )

        sharer = ActorLookup(sender_id).lookup()

        content = translate(
            _(
                u'share_mail_summary',
                default=u'${user} has sent you a notification:',
                mapping={'user': sharer.get_label()}
            ),
            context=self.request
        )

        comment_title = translate(
            _(
                u'share_mail_comment_title',
                default=u'Comment'
            ),
            context=self.request
        )

        data = {
            'title': target_object.title,
            'link': target_object.absolute_url(),
            'content': content.splitlines(),
            'comment_title': comment_title,
            'comment': comment.splitlines(),
        }
        msg, mail_to, mail_from = self.prepare_mail(
            subject=subject, to_email=to_email, cc_email=cc_email,
            bcc_email=bcc_email, from_userid=sender_id, data=data)

        self.send_mail(msg, mail_to, mail_from)
