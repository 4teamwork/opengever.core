from ftw.mail.exceptions import NoSenderFound
from ftw.mail.exceptions import UnknownSender
from ftw.mail.inbound import MailInbound
from opengever.mail.exceptions import MessageContainsVirus
from opengever.mail.interfaces import IInboundMailSettings
from opengever.virusscan.validator import validateUploadForFieldIfNecessary
from plone import api
from six import BytesIO
from zope.component import getMultiAdapter
from zope.interface import Invalid
import logging


log = logging.getLogger(__name__)


class GeverMailInbound(MailInbound):

    def msg(self):
        """We add scanning for viruses and raise an exception inheriting from
        MailInboundException, setting an appropriate exit code.
        """
        msg = super(GeverMailInbound, self).msg()
        filelike = BytesIO(msg)
        filename = '<stream>'

        try:
            validateUploadForFieldIfNecessary(
                'message', filename, filelike, self.request)
        except Invalid as e:
            raise MessageContainsVirus(e.message)
        return msg

    def get_sender_aliases(self):
        sender_aliases = api.portal.get_registry_record(
            'sender_aliases', interface=IInboundMailSettings)

        if not sender_aliases:
            # Dict records in p.a.registry may be returned as `None`
            sender_aliases = {}

        sender_aliases = {
            key.lower(): value for key, value in sender_aliases.items()
        }
        return sender_aliases

    def get_user(self):
        sender_email = self.sender()
        if not sender_email:
            log.warn("No sender found in 'Resent-From' or 'From' headers")
            raise NoSenderFound(self.msg())

        sender_aliases = self.get_sender_aliases()
        acl_users = api.portal.get_tool('acl_users')
        pas_search = getMultiAdapter((self.context, self.request),
                                     name='pas_search')
        matches = pas_search.searchUsers(email=sender_email, exact_match=False)

        if len(matches) > 0:
            # Matches from pas_search are fuzzy (and exact_match=True may only
            # be used when querying for 'id' or 'login'). We therefore filter
            # for exact (but case-insensitive) matches ourselves.
            for user_record in matches:
                user = self._get_user_by_id(acl_users, user_record['userid'])
                user_email = user.getProperty('email')
                if user_email.lower() == sender_email.lower():
                    return user

        if sender_email.lower() in sender_aliases:
            target_userid = sender_aliases[sender_email.lower()]
            log.info('Sender address %r is an alias for userid %r' % (
                sender_email, target_userid))
            user = self._get_user_by_id(acl_users, target_userid)
            if user:
                return user

        log.warn('Sender address: %r' % sender_email)
        log.warn('No users found in %r for that address.' % acl_users)
        raise UnknownSender(self.msg())

    def _get_user_by_id(self, acl_users, userid):
        user = acl_users.getUserById(userid)
        if user and not hasattr(user, 'aq_base'):
            user = user.__of__(acl_users)
        return user
