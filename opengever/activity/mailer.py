from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from opengever.base.model import get_locale
from opengever.mail.utils import make_addr_header
from opengever.ogds.base.utils import ogds_service
from pkg_resources import resource_filename
from plone import api


class Mailer(object):
    """Simple mixin, which helps to send mails, used by notification
    and digest mails.
    """

    def __init__(self):
        self.mailhost = api.portal.get_tool('MailHost')

        # This is required by ViewPageTemplateFile for
        # the html mail-template
        self.context = api.portal.get()
        self.request = self.context.REQUEST

    def send_mail(self, msg):
        self.mailhost.send(msg)

    def prepare_mail(self, subject=u'', to_userid=None, from_userid=None, data={}):
        msg = MIMEMultipart('related')

        if from_userid:
            actor = ogds_service().fetch_user(from_userid)
            msg['From'] = make_addr_header(actor.fullname(),
                                           actor.email, 'utf-8')
        else:
            msg['From'] = make_addr_header(
                u'OneGov GEVER', api.portal.get().email_from_address, 'utf-8')

        recipient = ogds_service().fetch_user(to_userid)
        msg['To'] = recipient.email
        msg['Subject'] = Header(subject, 'utf-8')

        html = self.prepare_html(data)
        msg.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))
        msg.attach(self.get_logo_part())
        return msg

    def get_users_language(self):
        # XXX TODO Right now there is no support to store users preferred
        # language. Therefore we send the mails always in the current selected
        # language.
        return get_locale()

    def get_logo_part(self):
        path = resource_filename(
            'opengever.activity.browser.resources', 'gever.png')
        fp = open(path, 'r')
        msg_image = MIMEImage(fp.read())
        fp.close()
        msg_image.add_header('Content-ID', '<image1>')
        return msg_image

    def prepare_html(self, data):
        return self.template(self, **data)
