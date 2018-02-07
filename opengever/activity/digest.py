from datetime import datetime
from opengever.activity.dispatcher import NotificationDispatcher
from opengever.activity.mailer import Mailer
from opengever.activity.model import Notification
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.activity")


class DigestDispatcher(NotificationDispatcher):

    _id = 'digest'
    roles_key = 'digest_notification_roles'

    def dispatch_notification(self, notification):
        notification.is_digest = True


class DigestMailer(Mailer):

    template = ViewPageTemplateFile("templates/digest.pt")

    def get_notifications(self):
        notifications = {}

        query = Notification.query.unsent_digest_notifications()
        for notification in query.all():
            if notification.userid in notifications:
                notifications[notification.userid].append(notification)
            else:
                notifications[notification.userid] = [notification]

        return notifications

    def group_by_resource(self, notifications):
        data = {}
        for notification in notifications:
            resource = notification.activity.resource
            if resource in data:
                data[resource].append(notification)
            else:
                data[resource] = [notification]

        return data

    def prepare_data(self, notifications):
        items = []
        language = self.get_users_language()
        data = self.group_by_resource(notifications).items()
        for resource, notifications in data:
            activities = [
                self.serialize_activity(notification.activity, language)
                for notification in notifications]
            items.append({
                'title': activities[0]['title'],
                'url': ResolveOGUIDView.url_for(resource.oguid),
                'activities': activities})
        return items

    def serialize_activity(self, activity, language):
        return {
            'title': activity.translations[language].title,
            'label': activity.translations[language].label,
            'summary': activity.translations[language].summary,
            'description': activity.translations[language].description}

    def send_digests(self):
        for userid, notifications in self.get_notifications().items():
            msg = self.prepare_mail(
                subject=_(u'subject_digest', default=u'Daily Digest'),
                to_userid=userid,
                data={'notifications': self.prepare_data(notifications),
                      'today': api.portal.get().unrestrictedTraverse(
                          'plone').toLocalizedTime(datetime.today())})
            self.send_mail(msg)
            self.mark_as_sent(notifications)

    def mark_as_sent(self, notifications):
        for notification in notifications:
            notification.sent_in_digest = True
