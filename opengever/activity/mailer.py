from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from opengever.activity.error_handling import NotificationErrorHandler
from opengever.base.interfaces import IOGMailSettings
from opengever.base.model import get_locale
from opengever.mail.utils import make_addr_header
from opengever.ogds.models.service import ogds_service
from plone import api
from Products.MailHost.MailHost import _mungeHeaders
from threading import local
import transaction


class NotificationMailQueue(local):
    """Thread-local mail queue that keeps track of mails to be sent at
    the end using a beforeCommitHook.
    """

    def __init__(self):
        self._queue = []

    def put(self, msg, mail_to, mail_from):
        self._queue.append((msg, mail_to, mail_from))

    def get(self):
        return self._queue.pop()

    def empty(self):
        return not len(self._queue)


mail_queue = NotificationMailQueue()


def process_mail_queue():
    mailhost = api.portal.get_tool('MailHost')

    with NotificationErrorHandler():
        while not mail_queue.empty():
            mail, mail_to, mail_from = mail_queue.get()

            # The MailHost `send` method overwrites the FROM and TO header
            # in the Message, if you pass in to and from adresses. But we
            # need to pass in the adresses to avoid problems with long or
            # fullnames with umlauts. Therefore we directly use the `_send`
            # method, and use _mungeHeaders only for the message text.
            messageText, _, _ = _mungeHeaders(mail)
            mailhost._send(mail_from, mail_to, messageText)


class Mailer(object):
    """Simple mixin, which helps to send mails, used by notification
    and digest mails.
    """

    default_addr_header = u'OneGov GEVER'

    def __init__(self):
        # This is required by ViewPageTemplateFile for
        # the html mail-template
        self.context = api.portal.get()
        self.request = self.context.REQUEST

        # Register beforeCommitHook that processes the mail queue at the
        # end of the transaction.
        txn = transaction.get()
        if process_mail_queue not in txn.getBeforeCommitHooks():
            txn.addBeforeCommitHook(process_mail_queue)

    def send_mail(self, msg, mail_to, mail_from):
        """Queue a mail for delivery at the end of the transaction.

        We don't immediately call mailhost.send() here, but instead place
        mails to be sent in a queue that gets processed at the end of the
        transaction.

        We need to do this because mailhost.send() registers an IDataManager
        without savepoint support (zope.sendmail.delivery.MailDataManager)
        on the transaction, in order to facilitate transactional mail support.

        This results in a 'Savepoints unsupported' TypeError if at any point
        after that data manager has joined the transaction any code tries to
        create a savepoint (creating initial versions does this for example).

        We therefore defer the dispatching of notification mails until the
        very end of the transaction to work around this issue.
        """
        mail_queue.put(msg, [each.strip() for each in mail_to.split(',')], mail_from)

    def prepare_mail(self, subject=u'', to_userid=None, to_email=None,
                     cc_email=None, from_userid=None, data=None):
        if data is None:
            data = {}

        msg = MIMEMultipart('related')

        actor = ogds_service().fetch_user(from_userid) if from_userid else None
        noreply_gever_address = api.portal.get().email_from_address
        from_mail = noreply_gever_address

        send_with_actor_from_address = api.portal.get_registry_record(
            name='send_with_actor_from_address', interface=IOGMailSettings)

        if actor:
            if not send_with_actor_from_address:
                # Set From: header to full name of actor, but 'noreply' address
                # of the GEVER deployment. Sending mails with the From-address of
                # the actor would lead to them getting rejected in modern mail
                # setup, e.g. when DKIM is being used.
                msg['From'] = make_addr_header(actor.fullname(),
                                               noreply_gever_address, 'utf-8')

                # Set the Reply-To header to the actual user's address
                msg['Reply-To'] = make_addr_header(actor.fullname(),
                                                   actor.email, 'utf-8')
            else:
                # Use the actor's email address for the From: header.
                # This might be caught in spam filters because it's effectively
                # sender address spoofing, but is sometimes desired by
                # customers for compatibility with autoresponders.
                msg['From'] = make_addr_header(actor.fullname(), actor.email, 'utf-8')
                from_mail = actor.email
        else:
            msg['From'] = make_addr_header(
                self.default_addr_header, noreply_gever_address, 'utf-8')

        if to_userid:
            to_email = ogds_service().fetch_user(to_userid).email
        msg['To'] = to_email
        if cc_email:
            msg['Cc'] = cc_email
        msg['Subject'] = Header(subject, 'utf-8')

        # Break (potential) description out into a list element per newline
        if data.get('description'):
            data['description'] = data.get('description').splitlines()

        html = self.prepare_html(data)
        msg.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))
        return msg, to_email, from_mail

    def get_users_language(self):
        # XXX TODO Right now there is no support to store users preferred
        # language. Therefore we send the mails always in the current selected
        # language.
        return get_locale()

    def prepare_html(self, data):
        return self.template(self, **data)
