from copy import deepcopy
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.kub.entity import KuBEntity
from opengever.kub.interfaces import IKuBSettings
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import InternalError
from zExceptions import NotFound
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


@implementer(ISerializeToJson)
@adapter(KuBEntity, IOpengeverBaseLayer)
class SerializeKuBEntityToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, full_representation=False):
        serialization = self.context.serialize()
        serialization['additional_ui_attributes'] = api.portal.get_registry_record(
            'additional_ui_attributes', interface=IKuBSettings)
        return serialization


class KuBGet(Service):
    """API Endpoint that returns a single user from ogds.

    GET /@kub/contact_uid HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(KuBGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        _id = self.read_params().decode('utf-8')
        try:
            entity = KuBEntity(_id)
            serializer = queryMultiAdapter((entity, self.request), ISerializeToJson)
        except LookupError:
            raise NotFound
        return serializer()

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply ID as URL path parameter.")

        return self.params[0]


class PersonContactSyncer(object):
    def __init__(self, kub_client):
        self.kub_client = kub_client

    def get_create_payload(self):
        payload = deepcopy(self.contact_data)

        # The username is not required but unique. We can't guarantee
        # a unique username between two kub installations. We have to
        # remove it before creating a new person
        if 'username' in payload:
            del payload['username']

        # We do not provide membership creation.
        if 'memberships' in payload:
            del payload['memberships']

        return payload

    def find_by_third_party_id(self):
        response = self.kub_client.list_people(filters={'third_party_id': self.third_party_id})
        if response['count'] == 1:
            return response["results"][0]
        return None

    def find_by_guessing(self):
        first_name = self.contact_data.get('firstName')
        official_name = self.contact_data.get('officialName')
        date_of_birth = self.contact_data.get('dateOfBirth')

        if not all((first_name, official_name, date_of_birth)):
            # Only guess if we have enough information
            return None

        response = self.kub_client.list_people(
            filters={
                'first_name': first_name,
                'official_name': official_name,
                'date_of_birth_max': date_of_birth,
                'date_of_birth_min': date_of_birth,
            }
        )
        if response['count'] == 1:
            return response["results"][0]
        return None

    def find_existing(self):
        return self.find_by_third_party_id() or self.find_by_guessing()

    def create(self):
        created_data = self.kub_client.create_person(self.get_create_payload())
        if created_data is None:
            raise InternalError('Creating person failed')
        return created_data

    def get_or_create_kub_obj(self):
        kub_obj = self.find_existing()
        if not kub_obj:
            kub_obj = self.create()
        return kub_obj

    def sync(self, contact_id, contact_data):
        """Tries to find a contact in the local KUB installation and returns
        its type-id. If no contact could be found, it will create a new one.
        """
        self.contact_data = contact_data
        self.third_party_id = contact_data.get('thirdPartyId') or contact_id
        kub_obj = self.get_or_create_kub_obj()
        return 'person:{}'.format(kub_obj['id'])


class OrganizationContactSyncer(object):
    def __init__(self, kub_client):
        self.kub_client = kub_client

    def get_create_payload(self):
        payload = deepcopy(self.contact_data)

        # We do not provide membership creation.
        if 'memberships' in payload:
            del payload['memberships']

        return payload

    def find_by_third_pary_id(self):
        response = self.kub_client.list_organizations(filters={'third_party_id': self.third_party_id})
        if response['count'] == 1:
            return response["results"][0]
        return None

    def find_by_guessing(self):
        name = self.contact_data.get('name')

        if not name:
            # Only guess if we have enough information
            return None

        response = self.kub_client.list_organizations(filters={'name': name})
        if response['count'] == 1:
            return response["results"][0]
        return None

    def find_existing(self):
        return self.find_by_third_pary_id() or self.find_by_guessing()

    def create(self):
        created_data = self.kub_client.create_organization(self.get_create_payload())
        if created_data is None:
            raise InternalError('Creating organization failed')
        return created_data

    def get_or_create_kub_obj(self):
        kub_obj = self.find_existing()
        if not kub_obj:
            kub_obj = self.create()
        return kub_obj

    def sync(self, contact_id, contact_data):
        self.contact_data = contact_data
        self.third_party_id = contact_data.get('thirdPartyId') or contact_id
        kub_obj = self.get_or_create_kub_obj()
        return 'organization:{}'.format(kub_obj['id'])
