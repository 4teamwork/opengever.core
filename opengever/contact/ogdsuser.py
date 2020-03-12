from opengever.contact import _
from opengever.contact.docprops import AddressDocPropertyProvider
from opengever.contact.docprops import MailAddressDocPropertyProvider
from opengever.contact.docprops import PersonDocPropertyProvider
from opengever.contact.docprops import PhoneNumberDocPropertyProvider
from opengever.contact.docprops import URLDocPropertyProvider
from opengever.ogds.base.browser.userdetails import UserDetails
from opengever.ogds.models.service import ogds_service


class BaseAdapter(object):
    """Provides equality support for all adapters.

    Also sets unique type-specific id based on the user id and a supplied
    index number.

    """
    id_attribute_name = None

    def __init__(self, user_id, index):
        identifier = '_'.join((str(user_id), str(index),))
        setattr(self, self.id_attribute_name, identifier)

    def _get_id(self):
        return getattr(self, self.id_attribute_name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(self._get_id())


class AddressAdapter(BaseAdapter):
    """Adapter that represents ogds user addresses as sql-contact
    addresses.

    """
    label = None
    id_attribute_name = 'address_id'

    def __init__(self, user_id, index, user_title, street, zip_code, city, country):
        super(AddressAdapter, self).__init__(user_id, index)
        self.user_title = user_title
        self.street = street
        self.zip_code = zip_code
        self.city = city
        self.country = country

    @property
    def has_data(self):
        return any((self.street, self.zip_code, self.city, self.country))

    def get_lines(self):
        """Return a list all address-lines that are not empty."""

        return [self.user_title,
                self.street,
                u" ".join(filter(None, [self.zip_code, self.city]))]

    def get_doc_property_provider(self):
        return AddressDocPropertyProvider(self)


class MailAddressAdapter(BaseAdapter):
    """Adapter that represents ogds user mail-addresses as sql-contact
    mail-addresses.

    """
    label = None
    id_attribute_name = 'mailaddress_id'

    def __init__(self, user_id, index, address):
        super(MailAddressAdapter, self).__init__(user_id, index)
        self.address = address

    @property
    def has_data(self):
        return bool(self.address)

    def get_doc_property_provider(self):
        return MailAddressDocPropertyProvider(self)


class PhoneNumberAdapter(BaseAdapter):
    """Adapter that represents ogds user phonenumbers as sql-contact
    phonenumbers.

    """
    id_attribute_name = 'phone_number_id'

    def __init__(self, user_id, index, phone_number, label):
        super(PhoneNumberAdapter, self).__init__(user_id, index)
        self.phone_number = phone_number
        self.label = label

    @property
    def has_data(self):
        return bool(self.phone_number)

    def get_doc_property_provider(self):
        return PhoneNumberDocPropertyProvider(self)


class URLAdapter(BaseAdapter):
    """Adapter that represents ogds user urls as sql-contact urls. """

    label = None
    id_attribute_name = 'url_id'

    def __init__(self, user_id, index, url):
        super(URLAdapter, self).__init__(user_id, index)
        self.url = url

    @property
    def has_data(self):
        return bool(self.url)

    def get_doc_property_provider(self):
        return URLDocPropertyProvider(self)


class OgdsUserToContactAdapter(BaseAdapter):
    """Adapter that represents ogds users as sql-contacts."""

    id_attribute_name = 'id'

    class QueryAdapter(object):
        """Adapter for query calls."""

        def get(self, userid):
            return OgdsUserToContactAdapter(ogds_service().find_user(userid))
    query = QueryAdapter()

    def __init__(self, ogds_user):
        self.ogds_user = ogds_user

    @property
    def id(self):
        return self.ogds_user.userid

    @property
    def is_adapted_user(self):
        return True

    def get_title(self, with_former_id=True):
        return self.ogds_user.label(with_principal=with_former_id)

    def get_url(self):
        return UserDetails.url_for(self.id)

    def get_css_class(self):
        return 'contenttype-person'

    @property
    def description(self):
        return self.ogds_user.description

    @property
    def salutation(self):
        return self.ogds_user.salutation

    @property
    def academic_title(self):
        return None

    @property
    def firstname(self):
        return self.ogds_user.firstname

    @property
    def lastname(self):
        return self.ogds_user.lastname

    def get_doc_property_provider(self):
        return PersonDocPropertyProvider(self)

    @property
    def addresses(self):
        index = 1
        address_adapter = AddressAdapter(
                self.id,
                index,
                self.get_title(with_former_id=False),
                u", ".join(filter(None, [self.ogds_user.address1,
                                         self.ogds_user.address2])),
                self.ogds_user.zip_code,
                self.ogds_user.city,
                self.ogds_user.country,)

        if not address_adapter.has_data:
            return []
        return [address_adapter]

    @property
    def mail_addresses(self):
        result = []
        for index, mail_address in enumerate(
                [self.ogds_user.email, self.ogds_user.email2], 1):
            adapter = MailAddressAdapter(self.id, index, mail_address)
            if adapter.has_data:
                result.append(adapter)
        return result

    @property
    def phonenumbers(self):
        result = []
        for index, data in enumerate([
                (_('label_office', default='Office'), self.ogds_user.phone_office),
                (_('label_fax', default="Fax"), self.ogds_user.phone_fax),
                (_('label_mobile', default="Mobile"), self.ogds_user.phone_mobile)],
                1):
            label, phone_number = data
            adapter = PhoneNumberAdapter(self.id, index, phone_number, label)
            if adapter.has_data:
                result.append(adapter)
        return result

    @property
    def urls(self):
        index = 1
        adapter = URLAdapter(self.id, index, self.ogds_user.url)
        if not adapter.has_data:
            return []
        return [adapter]
