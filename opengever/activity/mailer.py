from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from opengever.activity.error_handling import NotificationErrorHandler
from opengever.base.model import get_locale
from opengever.mail.utils import make_addr_header
from opengever.ogds.models.service import ogds_service
from plone import api
from threading import local
import transaction


class NotificationMailQueue(local):
    """Thread-local mail queue that keeps track of mails to be sent at
    the end using a beforeCommitHook.
    """

    def __init__(self):
        self._queue = []

    def put(self, msg):
        self._queue.append(msg)

    def get(self):
        return self._queue.pop()

    def empty(self):
        return not len(self._queue)


mail_queue = NotificationMailQueue()


def process_mail_queue():
    mailhost = api.portal.get_tool('MailHost')

    with NotificationErrorHandler():
        while not mail_queue.empty():
            mail = mail_queue.get()
            mailhost.send(mail)


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

    def send_mail(self, msg):
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
        mail_queue.put(msg)

    def prepare_mail(self, subject=u'', to_userid=None, to_email=None,
                     from_userid=None, data=None):
        if data is None:
            data = {}

        msg = MIMEMultipart('related')

        actor = ogds_service().fetch_user(from_userid) if from_userid else None
        noreply_gever_address = api.portal.get().email_from_address

        if actor:
            # Set From: header to full name of actor, but 'noreply' address
            # of the GEVER deployment. Sending mails with the From-address of
            # the actor would lead to them getting rejected in modern mail
            # setup, e.g. when DKIM is being used.
            msg['From'] = make_addr_header(actor.fullname(),
                                           noreply_gever_address, 'utf-8')
        else:
            msg['From'] = make_addr_header(
                self.default_addr_header, noreply_gever_address, 'utf-8')

        if to_userid:
            to_email = ogds_service().fetch_user(to_userid).email
        msg['To'] = to_email
        msg['Subject'] = Header(subject, 'utf-8')

        # Break (potential) description out into a list element per newline
        if data.get('description'):
            data['description'] = data.get('description').splitlines()

        html = self.prepare_html(data)
        msg.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))
        return msg

    def get_users_language(self):
        # XXX TODO Right now there is no support to store users preferred
        # language. Therefore we send the mails always in the current selected
        # language.
        return get_locale()

    def prepare_html(self, data):
        return self.template(self, **data)
