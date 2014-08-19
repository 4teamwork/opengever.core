from ftw.inflator.creation.sections.jsonsource import recursive_encode
from opengever.ogds.base.utils import create_session
import json


class UnitCreator(object):

    def __init__(self, path):
        self.path = path
        self.session = create_session()

    def get_json_data(self):
        with open(self.path) as file_:
            data = json.loads(file_.read())

        for item in data:
            yield recursive_encode(item)

    def run(self):
        for item in self.get_json_data():
            self.create_unit(item)

    def create_unit(self, item):
        raise NotImplementedError()
