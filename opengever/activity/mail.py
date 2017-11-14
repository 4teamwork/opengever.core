from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from opengever.activity.browser import resolve_notification_url
from opengever.activity.dispatcher import NotificationDispatcher
from opengever.base.model import get_locale
from opengever.mail.utils import make_addr_header
from opengever.ogds.base.utils import ogds_service
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory


# because of circular imports, we can't import from opengever.activity
_ = MessageFactory("opengever.activity")


class PloneNotificationMailer(NotificationDispatcher):
    """The PloneNotificationMailer is a notification dispatcher,
    which generates mail(s) for passed notification(s) and send them to
    the corresponding watcher.
    """

    roles_key = 'mail_notification_roles'

    def __init__(self):
        self.mailhost = api.portal.get_tool('MailHost')

        # This is required by ViewPageTemplateFile for
        # the html mail-template
        self.context = api.portal.get()
        self.request = self.context.REQUEST

    def dispatch_notification(self, notification):
        msg = self.prepare_mail(notification)
        self.send_mail(msg)

    def send_mail(self, msg):
        self.mailhost.send(msg)

    def prepare_mail(self, notification):
        msg = MIMEMultipart('alternative')

        actor = ogds_service().fetch_user(notification.activity.actor_id)
        msg['From'] = make_addr_header(actor.fullname(), actor.email, 'utf-8')

        recipient = ogds_service().fetch_user(notification.userid)
        msg['To'] = recipient.email
        msg['Subject'] = self.get_subject(notification)

        html = self.prepare_html(notification)
        msg.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))

        return msg

    def get_subject(self, notification):
        prefix = translate(_(u'subject_prefix', default=u'GEVER Task'),
                           context=self.request)
        title = notification.activity.translations[self.get_users_language()].title
        return Header(u'{}: {}'.format(prefix, title), 'utf-8')

    def get_users_language(self):
        # XXX TODO Right now there is no support to store users preferred
        # language. Therefore we send the mails always in the current selected
        # language.
        return get_locale()

    def prepare_html(self, notification):
        template = ViewPageTemplateFile("templates/notification.pt")
        language = self.get_users_language()
        options = {
            'title': notification.activity.translations[language].title,
            'label': notification.activity.translations[language].label,
            'summary': notification.activity.translations[language].summary,
            'description': notification.activity.translations[language].description,
            'link': resolve_notification_url(notification)
        }

        return template(self, **options)
