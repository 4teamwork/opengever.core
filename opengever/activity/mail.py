from Acquisition import aq_inner
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from opengever.ogds.base.utils import ogds_service
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NotificationMailer(object):

    def __init__(self, context, notification):
        self.context = aq_inner(context)
        self.request = self.context.REQUEST
        self.notification = notification

    def send_mail(self):
        msg = self.prepare_mail()
        mailhost = api.portal.get_tool('MailHost')
        mailhost.send(msg)

    def prepare_mail(self):
        msg = MIMEMultipart('alternative')

        actor = ogds_service().fetch_user(self.notification.activity.actor_id)
        msg['From'] = Header(u'{} <{}>'.format(actor.fullname(), actor.email),
                             'utf-8')

        recipient = ogds_service().fetch_user(
            self.notification.watcher.user_id)
        msg['To'] = recipient.email
        msg['Subject'] = Header(self.notification.activity.title, 'utf-8')

        html = self.prepare_html()
        msg.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))

        return msg

    def prepare_html(self):

        # Todo: solve circular dependency
        from opengever.activity.browser.resolve import ResolveNotificationView
        template = ViewPageTemplateFile("mail_templates/notification.pt")
        options = {
            'subject': self.notification.activity.title,
            'title': self.notification.activity.title,
            'kind': self.notification.activity.kind,
            'summary': self.notification.activity.summary,
            'description': self.notification.activity.description,
            'link': ResolveNotificationView.url_for(self.notification.notification_id)
        }

        return template(self, **options)
