from opengever.kub.client import KuBClient
from opengever.kub.docprops import KuBEntityDocPropertyProvider


class KuBEntity(object):

    def __init__(self, type_id, full=False):
        self.identifier = type_id
        if full:
            self.data = KuBClient().get_full_entity_by_id(self.identifier)
        else:
            self.data = KuBClient().get_by_id(self.identifier)

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def serialize(self):
        return self.data

    def is_person(self):
        return self.get("type") == "person"

    def is_organization(self):
        return self.get("type") == "organization"

    def is_membership(self):
        return self.get("type") == "membership"

    def get_doc_property_provider(self):
        return KuBEntityDocPropertyProvider(self)