from doctest import Example
from lxml.doctestcompare import LXMLOutputChecker
from opengever.propertysheets.exportimport import BaseHandler
from opengever.propertysheets.exportimport import dottedname
from opengever.testing import IntegrationTestCase
from plone.supermodel import loadString
from plone.supermodel import serializeSchema
from plone.supermodel.exportimport import BaseHandler as PSBaseHandler
from plone.supermodel.interfaces import IFieldExportImportHandler
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import provider
from zope.schema import Choice
from zope.schema.interfaces import IContextAwareDefaultFactory
import inspect
import unittest


@provider(IContextAwareDefaultFactory)
def dummy_default_factory(context):
    return 'de'


class TestSupermodelExportImport(IntegrationTestCase):

    MODEL_XMLNS = """\
    xmlns:form="http://namespaces.plone.org/supermodel/form" \
    xmlns:i18n="http://xml.zope.org/namespaces/i18n" \
    xmlns:indexer="http://namespaces.plone.org/supermodel/indexer" \
    xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" \
    xmlns:security="http://namespaces.plone.org/supermodel/security" \
    xmlns="http://namespaces.plone.org/supermodel/schema"\
    """

    def assertSchemaXMLEqual(self, expected, actual):
        # Discard the outer <model /> node with all its messy namespaces
        actual = '\n'.join(actual.split('\n')[1:-1])

        checker = LXMLOutputChecker()
        if not checker.check_output(expected, actual, 0):
            message = checker.output_difference(Example("", expected), actual, 0)
            raise AssertionError(message)

    def test_serializes_default_factory(self):

        class SchemaWithDefaultFactory(Interface):

            language = Choice(
                title=u'Language',
                values=['de', 'fr'],
                defaultFactory=dummy_default_factory,
            )

        dottedname = '.'.join([__name__, 'dummy_default_factory'])
        expected = """\
            <schema name="Dummy" based-on="zope.interface.Interface">
              <field name="language" type="zope.schema.Choice">
                <default>de</default>
                <defaultFactory>%s</defaultFactory>
                <title>Language</title>
                <values>
                  <element>de</element>
                  <element>fr</element>
                </values>
              </field>
            </schema>
        """ % dottedname

        serialized_schema = serializeSchema(SchemaWithDefaultFactory, name='Dummy')
        self.assertSchemaXMLEqual(expected, serialized_schema)

    def test_deserializes_default_factory(self):
        """Test deserialization of defaultFactories via dottedname.

        This already works in stock plone.supermodel, without any of our
        customiztations. Let's make sure it keeps working.
        """
        dottedname = '.'.join([__name__, 'dummy_default_factory'])
        xml_schema = """\
        <model %s>
          <schema name="Dummy" based-on="zope.interface.Interface">
            <field name="language" type="zope.schema.Choice">
              <default>de</default>
              <defaultFactory>%s</defaultFactory>
              <title>Language</title>
              <values>
                <element>de</element>
                <element>fr</element>
              </values>
            </field>
          </schema>
        </model>
        """ % (self.MODEL_XMLNS, dottedname)

        model = loadString(xml_schema)
        deserialized_schema = model.schemata['Dummy']
        self.assertEqual(
            dummy_default_factory,
            deserialized_schema['language'].defaultFactory)


class TestSupermodelHandlerOverrides(IntegrationTestCase):

    def test_plone_supermodel_handlers_are_overridden(self):
        field_types = (
            'zope.schema.Bytes',
            'zope.schema.ASCII',
            'zope.schema.BytesLine',
            'zope.schema.ASCIILine',
            'zope.schema.Text',
            'zope.schema.TextLine',
            'zope.schema.Bool',
            'zope.schema.Int',
            'zope.schema.Float',
            'zope.schema.Decimal',
            'zope.schema.Tuple',
            'zope.schema.List',
            'zope.schema.Set',
            'zope.schema.FrozenSet',
            'zope.schema.Password',
            'zope.schema.Dict',
            'zope.schema.Datetime',
            'zope.schema.Date',
            'zope.schema.SourceText',
            'zope.schema.URI',
            'zope.schema.Id',
            'zope.schema.DottedName',
            'zope.schema.InterfaceField',
            'zope.schema.Object',
            'zope.schema.Choice',
        )
        for ft in field_types:
            handler = getUtility(IFieldExportImportHandler, name=ft)
            expected_module = 'opengever.propertysheets.exportimport'

            self.assertEqual(
                'opengever.propertysheets.exportimport', handler.__module__,
                "The plone.supermodel IFieldExportImportHandler for %r should "
                "be overridden by a handler in %s, but it appears that it "
                "isn't" % (ft, expected_module))

            self.assertTrue(
                issubclass(handler.__class__, BaseHandler),
                "%r doesn't seem to use our own BaseHandler. Overridden "
                "IFieldExportImportHandlers should either be direct instances "
                "of our own custom BaseHandler, or subclass it." % ft)

            if handler.__class__ is not BaseHandler:
                mro = inspect.getmro(handler.__class__)
                our_basehandler_pos = mro.index(BaseHandler)
                plone_basehandler_pos = mro.index(PSBaseHandler)

                # This test makes sure MRO is set up in a way that method /
                # attribute lookups find our own BaseHandler's methods first,
                # even in cases where plone.supermodel's BaseHandler also is
                # part of the inheritance hierarchy.
                #
                # This allows us to subclass p.supermodels more specific
                # handlers, like ChoiceHandler, instead of having to copy
                # them over in their entirety.

                self.assertTrue(
                    our_basehandler_pos < plone_basehandler_pos,
                    "Our own BaseHandler should appear before "
                    "plone.supermodel's in the handler's MRO, but it doesn't.")


def module_global_func(arg):
    pass


class DummyClass(object):

    @staticmethod
    def static_method(arg):
        pass


class TestDottednameHelper(unittest.TestCase):

    def test_dottedname_resolves_func_in_module_scope(self):
        self.assertEqual(
            'opengever.propertysheets.tests.test_exportimport.module_global_func',
            dottedname(module_global_func))

    def test_dottedname_doesnt_resolve_static_methods(self):
        self.assertIsNone(dottedname(DummyClass.static_method))

    def test_dottedname_doesnt_resolve_func_in_nested_scope(self):

        def myfunc(arg):
            pass

        self.assertIsNone(dottedname(myfunc))

    def test_dottedname_doesnt_resolve_lambdas(self):
        self.assertIsNone(dottedname(lambda arg: arg))
