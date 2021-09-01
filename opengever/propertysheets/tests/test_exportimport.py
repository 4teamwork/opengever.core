from opengever.propertysheets.exportimport import BaseHandler
from opengever.testing import IntegrationTestCase
from plone.supermodel.exportimport import BaseHandler as PSBaseHandler
from plone.supermodel.interfaces import IFieldExportImportHandler
from zope.component import getUtility
import inspect


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
