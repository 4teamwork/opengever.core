from ftw.inflator.creation.sections.jsonsource import recursive_encode
from opengever.ogds.base.utils import create_session
from opengever.setup.exception import GeverSetupException
import json


class UnitCreator(object):

    item_name = None
    item_class = None
    required_attributes = tuple()

    def __init__(self):
        self.session = create_session()

    def get_json_data(self, jsonfile):
        data = json.loads(jsonfile.read())

        for item in data:
            yield recursive_encode(item)

    def run(self, jsonfile):
        for item in self.get_json_data(jsonfile):
            self.check_constraints(item)
            self.create_unit(item)

    def check_constraints(self, item):
        for attribute in self.required_attributes:
            if attribute not in item:
                msg = "Attribute '{}' is required for {}".format(
                    attribute, self.item_name)
                raise GeverSetupException(msg)

    def create_unit(self, item):
        self.session.add(self.item_class(**item))
