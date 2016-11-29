from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.setup.sections.jsonsource import JSONSourceSection
from pkg_resources import resource_filename
from unittest2 import TestCase
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestJSONSource(TestCase):

    def setup_source(self, options, previous=None):
        previous = previous or []
        options.setdefault('blueprint', 'opengever.setup.jsonsource')
        return JSONSourceSection(None, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(JSONSourceSection))
        verifyClass(ISection, JSONSourceSection)

        self.assertTrue(ISectionBlueprint.providedBy(JSONSourceSection))
        verifyObject(ISectionBlueprint, JSONSourceSection)

    def test_skips_missing_files(self):
        directory = resource_filename('opengever.setup.tests', 'nope')
        source = self.setup_source({'json_dir': directory,
                                    'filename': 'nope.json'},
                                   previous=['Foo'])

        self.assertEqual(['Foo'], list(source))

    def test_json_file_parsing(self):
        directory = resource_filename('opengever.setup.tests', 'assets')
        source = self.setup_source({'json_dir': directory,
                                    'filename': 'simple.json'})
        self.assertEqual(
            [{u'_source': 'simple.json', u'item': u'b\xe4r'}], list(source)
        )

    def test_inserts_portal_type_if_specified(self):
        directory = resource_filename('opengever.setup.tests', 'assets')
        source = self.setup_source(
            {'json_dir': directory,
             'filename': 'simple.json',
             'portal_type': 'foo.bar.qux'})
        self.assertEqual(
            [{u'item': u'b\xe4r',
              u'_source': 'simple.json',
              u'_type': 'foo.bar.qux'}],
            list(source)
        )
