from datetime import datetime
from ftw.mail import utils


def get_header_date(mail):
    return datetime.fromtimestamp(utils.get_date_header(mail.msg, 'Date'))
