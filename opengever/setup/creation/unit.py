from ftw.inflator.creation.sections.jsonsource import recursive_encode
from opengever.base.model import create_session
from opengever.setup.exception import GeverSetupException
import json


class UnitCreator(object):

    item_name = None
    item_class = None
    required_attributes = tuple()
    key_mapping = {}

    def __init__(self, is_development=False):
        self.session = create_session()
        self.is_development = is_development

    def get_json_data(self, jsonfile):
        data = json.loads(jsonfile.read())

        for item in data:
            yield recursive_encode(item)

    def run(self, jsonfile):
        for item in self.get_json_data(jsonfile):
            if self.is_development:
                self.apply_development_config(item)
            self.check_constraints(item)
            self.apply_key_mapping(item)
            self.create_unit(item)

    def apply_development_config(self, item):
        pass

    def apply_key_mapping(self, item):
        for key, new_key in self.key_mapping.items():
            if key not in item:
                continue

            item[new_key] = item[key]
            del item[key]

    def check_constraints(self, item):
        for attribute in self.required_attributes:
            if attribute not in item:
                msg = "Attribute '{}' is required for {}".format(
                    attribute, self.item_name)
                raise GeverSetupException(msg)

    def create_unit(self, item):
        self.session.add(self.item_class(**item))
