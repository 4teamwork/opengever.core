from zeep.client import Client
from zope.interface import implements

from opengever.briefbutler.interfaces import IBriefButler
from opengever.ogds.base.utils import get_current_admin_unit

WSDL_URL = 'http://www.moabox.at/docspool/services/DualSpoolService?wsdl'


class BriefButler(object):

    implements(IBriefButler)

    def __init__(self):
        self._client = None
        self._physical_person = None
        self._postal_address = None
        self._receiver = None
        self._legal_person = None
        self._sender = None
        self._binary_document = None

    def client():
        doc = "The cleint for the SOAP interface"

        def fget(self):
            if self._client is None:
                self._client = Client(WSDL_URL)
            return self._client

        def fset(self, value):
            self._client = value

        return locals()
    client = property(**client())

    @property
    def PhysicalPerson(self):
        if self._physical_person is None:
            self._physical_person = self.client.get_type('ns0:physicalPerson')
        return self._physical_person

    @property
    def PostalAddress(self):
        if self._postal_address is None:
            self._postal_address = self.client.get_type('ns0:postalAddress')
        return self._postal_address

    @property
    def Receiver(self):
        if self._receiver is None:
            self._receiver = self.client.get_type('ns0:receiver')
        return self._receiver

    @property
    def LegalPerson(self):
        if self._legal_person is None:
            self._legal_person = self.client.get_type('ns0:legalPerson')
        return self._legal_person

    @property
    def Sender(self):
        if self._sender is None:
            self._sender = self.client.get_type('ns0:sender')
        return self._sender

    @property
    def BinaryDocument(self):
        if self._binary_document is None:
            self._binary_document = self.client.get_type('ns0:binaryDocument')
        return self._binary_document

    def document(self, doc):
        _file = doc.get_file()

        kwargs = {'mimetype': getattr(_file, 'contentType'),
                  'name': getattr(_file, 'filename')}

        with _file.open() as _data:
            kwargs['content'] = _data.read()

        return self.BinaryDocument(**kwargs)

    def legal_person(self, data, prefix):
        return self.LegalPerson(
            firmenBuchNr=data.get('{0}_company_number'.format(prefix)),
            name=data.get('{0}_company_name'.format(prefix))
        )

    def physical_person(self, data, prefix):
        return self.PhysicalPerson(
            familyName=data.get('{0}_family_name'.format(prefix)),
            givenName=data.get('{0}_given_name'.format(prefix)),
        )

    def postal_address(self, data, prefix):
        return self.PostalAddress(
            street=data.get('{0}_street'.format(prefix)),
            postalCode=data.get('{0}_postal_code'.format(prefix)),
            city=data.get('{0}_city'.format(prefix)),
            countryCode='CH',
        )

    def receiver(self, data, prefix):
        physical_person = self.physical_person(data, prefix)
        postal_address = self.postal_address(data, prefix)
        return self.Receiver(allowEmail=True,
                             email=data.get('{0}_email'.format(prefix)),
                             physicalPerson=physical_person,
                             postalAddress=postal_address)

    def sender(self, data, prefix):
        legal_person = self.legal_person(data, prefix)
        postal_address = self.postal_address(data, prefix)
        return self.Sender(legalPerson=legal_person,
                           # yes... postalAdress with only one "d"!!
                           postalAdress=postal_address)

    def send(self, document, data):
        receiver = self.receiver(data, prefix='recipient')
        sender = self.sender(data, prefix='sender')
        _document = self.document(document)

        document_id = '{admin_unit}::{document_id}'.format(
            admin_unit=getattr(get_current_admin_unit(), 'title'),
            document_id=getattr(document, 'id'),
        )

        self.client.service.deliver(
            documentID=document_id,
            senderProfileID="profile-reg1",
            receiver=receiver,
            sender=sender,
            document=_document,
        )
