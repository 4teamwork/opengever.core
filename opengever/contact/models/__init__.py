from opengever.contact.models.address import Address  # noqa
from opengever.contact.models.archivedaddress import ArchivedAddress  # noqa
from opengever.contact.models.archivedcontact import ArchivedContact  # noqa
from opengever.contact.models.archivedmailaddress import ArchivedMailAddress  # noqa
from opengever.contact.models.archivedorganization import ArchivedOrganization  # noqa
from opengever.contact.models.archivedperson import ArchivedPerson  # noqa
from opengever.contact.models.archivedphonenumber import ArchivedPhoneNumber  # noqa
from opengever.contact.models.archivedurl import ArchivedURL  # noqa
from opengever.contact.models.contact import Contact  # noqa
from opengever.contact.models.mailaddress import MailAddress  # noqa
from opengever.contact.models.org_role import OrgRole  # noqa
from opengever.contact.models.organization import Organization  # noqa
from opengever.contact.models.participation import ContactParticipation  # noqa
from opengever.contact.models.participation import OgdsUserParticipation  # noqa
from opengever.contact.models.participation import OrgRoleParticipation  # noqa
from opengever.contact.models.participation import Participation  # noqa
from opengever.contact.models.participation_role import ParticipationRole  # noqa
from opengever.contact.models.person import Person  # noqa
from opengever.contact.models.phonenumber import PhoneNumber  # noqa
from opengever.contact.models.url import URL  # noqa
import opengever.contact.models.query  # noqa keep, initializes query classes!


tables = [
    'addresses',
    'archived_addresses',
    'archived_contacts',
    'archived_mail_addresses',
    'archived_organizations',
    'archived_persons',
    'archived_phonenumbers',
    'archived_urls',
    'contacts',
    'mail_addresses',
    'org_roles',
    'organizations',
    'participation_roles',
    'participations',
    'persons',
    'phonenumbers',
    'urls',
]
