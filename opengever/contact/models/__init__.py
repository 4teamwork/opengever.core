from opengever.contact.models.address import Address  # noqa
from opengever.contact.models.archivedaddress import ArchivedAddress  # noqa
from opengever.contact.models.archivedcontact import ArchivedContact  # noqa
from opengever.contact.models.archivedmailaddress import ArchivedMailAddress  # noqa
from opengever.contact.models.archivedperson import ArchivedPerson  # noqa
from opengever.contact.models.archivedphonenumber import ArchivedPhoneNumber  # noqa
from opengever.contact.models.archivedurl import ArchivedURL  # noqa
from opengever.contact.models.contact import Contact  # noqa
from opengever.contact.models.mailaddress import MailAddress  # noqa
from opengever.contact.models.person import Person  # noqa
from opengever.contact.models.phonenumber import PhoneNumber  # noqa
from opengever.contact.models.url import URL  # noqa
import opengever.contact.models.query  # noqa keep, initializes query classes!


tables = [
    'addresses',
    'archived_addresses',
    'archived_contacts',
    'archived_mail_addresses',
    'archived_persons',
    'archived_phonenumbers',
    'archived_urls',
    'contacts',
    'mail_addresses',
    'persons',
    'phonenumbers',
    'urls',
]
