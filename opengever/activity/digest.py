from datetime import date
from datetime import timedelta
from opengever.activity.dispatcher import NotificationDispatcher
from opengever.activity.mailer import Mailer
from opengever.activity.model import Digest
from opengever.activity.model import Notification
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import create_session
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
import logging


logger = logging.getLogger('opengever.activity.digest')
logger.setLevel(logging.INFO)

_ = MessageFactory("opengever.activity")

DIGEST_INTERVAL_HOURS = 24

DIGEST_TOLERANCE = 1


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
        logger.info('Sending digests...')
        for userid, notifications in self.get_notifications().items():
            # skip when digest interval is not expired yet
            if not self.is_interval_expired(userid):
                continue

            today = api.portal.get_localized_time(date.today())
            user = ogds_service().fetch_user(userid)

            subject = translate(
                _(u'subject_digest',
                  default=u'Daily Digest for ${date}',
                  mapping={'date': today}),
                context=self.request)
            title = translate(
                _(u'title_daily_digest',
                  default=u'Daily Digest for ${username}',
                  mapping={'username': user.fullname()}),
                context=self.request)
            msg = self.prepare_mail(
                subject=subject,
                to_userid=userid,
                data={'notifications': self.prepare_data(notifications),
                      'public_url': get_current_admin_unit().public_url,
                      'title': title,
                      'today': today})

            self.send_mail(msg)
            self.mark_as_sent(notifications)
            self.record_digest(userid)
            logger.info('  Digest sent for %s (%s)' % (userid, user.email))

        logger.info('Done sending digests.')

    def mark_as_sent(self, notifications):
        for notification in notifications:
            notification.sent_in_digest = True

    def record_digest(self, userid):
        digest = Digest.query.get_by_userid(userid)
        if not digest:
            digest = Digest(userid=userid, last_dispatch=utcnow_tz_aware())
            create_session().add(digest)

        digest.last_dispatch = utcnow_tz_aware()

    def is_interval_expired(self, userid):
        """Returns true it the time since the last dispatch expires the defined
        interval for the given user.

        The calculation has been made with a tolerance of 1 hour.
        """

        digest = Digest.query.get_by_userid(userid)
        if not digest:
            # no digests sent yet, so digest schould be send
            return True

        interval = timedelta(hours=DIGEST_INTERVAL_HOURS - DIGEST_TOLERANCE)
        expired = utcnow_tz_aware() - interval

        return digest.last_dispatch <= expired
