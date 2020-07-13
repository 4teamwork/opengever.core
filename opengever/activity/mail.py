from opengever.activity.browser import resolve_notification_url
from opengever.activity.dispatcher import NotificationDispatcher
from opengever.activity.mailer import Mailer
from opengever.ogds.base.utils import get_current_admin_unit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory


# because of circular imports, we can't import from opengever.activity
_ = MessageFactory("opengever.activity")


class PloneNotificationMailer(NotificationDispatcher, Mailer):
    """The PloneNotificationMailer is a notification dispatcher,
    which generates mail(s) for passed notification(s) and send them to
    the corresponding watcher.
    """

    _id = 'mail'
    roles_key = 'mail_notification_roles'
    template = ViewPageTemplateFile("templates/notification.pt")

    def dispatch_notification(self, notification):
        data = self.get_data(notification)
        msg = self.prepare_mail(
            subject=data.get('subject'),
            to_userid=notification.userid,
            from_userid=notification.activity.actor_id,
            data=data
        )
        self.send_mail(msg)

    def get_subject(self, notification_data):
        prefix = translate(_(u'subject_prefix', default=u'GEVER Activity'),
                           context=self.request)
        title = notification_data.get('title')
        return u'{}: {}'.format(prefix, title)

    def get_data(self, notification):
        data = notification.activity.serialize(with_description=True)
        data.update({
            'subject': self.get_subject(data),
            'link': resolve_notification_url(notification),
            'public_url': get_current_admin_unit().public_url})
        return data
