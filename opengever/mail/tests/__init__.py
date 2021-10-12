from pkg_resources import resource_string


MAIL_DATA = resource_string('opengever.mail.tests', 'mail.txt')
MAIL_DATA_WITH_AD_FROM_HEADER = resource_string('opengever.mail.tests', 'mail_with_ad_from.txt')
