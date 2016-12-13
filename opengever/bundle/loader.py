from collections import OrderedDict
import codecs
import json
import os


BUNDLE_JSON_TYPES = OrderedDict([
    ('reporoots.json', 'opengever.repository.repositoryroot'),
    ('repofolders.json', 'opengever.repository.repositoryfolder'),
    ('dossiers.json', 'opengever.dossier.businesscasedossier'),
    ('documents.json', 'opengever.document.document'),   # document or mail
])


class BundleLoader(object):
    """Loads an OGGBundle from the filesystem and yields the contained items
    in proper order.

    The loader also takes care of inserting the appropriate portal_type for
    each item.
    """

    def __init__(self, bundle_path):
        self.bundle_path = bundle_path

    def determine_portal_type(self, json_name, item):
        """Determine what portal_type an item should be, based on the name of
        the JSON file it's been read from.
        """
        if json_name == 'documents.json':
            filepath = item['filepath']
            if filepath is not None and filepath.endswith('.eml'):
                return 'ftw.mail.mail'
            return 'opengever.document.document'
        return BUNDLE_JSON_TYPES[json_name]

    def __iter__(self):
        """Yield all items of the bundle in order.
        """
        for json_name, portal_type in BUNDLE_JSON_TYPES.items():
            json_path = os.path.join(self.bundle_path, json_name)

            with codecs.open(json_path, 'r', 'utf-8-sig') as json_file:
                items = json.load(json_file)

            for item in items:
                item['_type'] = self.determine_portal_type(json_name, item)
                yield item
