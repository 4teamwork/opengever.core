from Products.CMFCore.interfaces import ISiteRoot
from grokcore.component.testing import grok
from mocker import ANY
from mocker import Mocker
from opengever.base.behaviors import lifecycle
from opengever.base.interfaces import IBaseCustodyPeriods
from plone.mocktestcase import MockTestCase
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IValue
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.interface import directlyProvides
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import VocabularyRegistryError
from zope.schema.vocabulary import getVocabularyRegistry


class TestCustodyPeriod(MockTestCase, TestCase):

    def setUp(self):
        super(TestCustodyPeriod, self).setUp()

        self.testcase_mocker = Mocker()
        grok('opengever.base.behaviors.lifecycle')

        # mock the registry, so that we have a static
        # configuration in our tests. we test functionality,
        # not configuration..
        proxy = self.testcase_mocker.mock()
        proxy.custody_periods
        self.testcase_mocker.result([u'0', u'10', u'20', u'30'])
        self.testcase_mocker.count(0, None)

        registry = self.testcase_mocker.mock()
        provideUtility(provides=IRegistry, component=registry)
        registry.forInterface(IBaseCustodyPeriods)
        self.testcase_mocker.result(proxy)
        self.testcase_mocker.count(0, None)

        # we need to register the vocabulary utility in the
        # vocabulary registry manually at this point:
        vocabulary_registry = getVocabularyRegistry()
        field = lifecycle.ILifeCycle['custody_period']
        try:
            vocabulary_registry.get(None, field.vocabularyName)
        except VocabularyRegistryError:
            factory = getUtility(IVocabularyFactory,
                                 name=u'lifecycle_custody_period_vocabulary')
            vocabulary_registry.register(field.vocabularyName, factory)

        # in this stage, only the grok-components (adapaters, utilities)
        # of the module are registered in the component registry.

        # we need to register any plone.directives.form magic components
        # from the module manually (they are not grokky):
        for factory, name in lifecycle.__form_value_adapters__:
            provideAdapter(factory, name=name)

        self.testcase_mocker.replay()

    def tearDown(self):
        self.testcase_mocker.verify()
        self.testcase_mocker.restore()
        super(TestCustodyPeriod, self).tearDown()

    def _get_term_titles_from_vocabulary(self, voc):
        return [term.title for term in voc._terms]

    def test_configured_field_vocabulary_factory_name(self):
        field = lifecycle.ILifeCycle['custody_period']
        self.assertEqual(field.vocabularyName,
                         u'lifecycle_custody_period_vocabulary')

    def test_vocabulary(self):
        vocfactory = getUtility(IVocabularyFactory,
                                name=u'lifecycle_custody_period_vocabulary')
        self.assertEqual(vocfactory.option_names, [0, 10, 20, 30])

    def test_vocabulary_in_context(self):
        vocfactory = getUtility(IVocabularyFactory,
                                name=u'lifecycle_custody_period_vocabulary')

        request = self.mocker.mock()
        self.expect(request.get('PATH_INFO', ANY)).result('somepath/++add++type')

        context = self.mocker.mock()
        self.expect(context.REQUEST).result(request)
        self.expect(context.custody_period).result(20)

        self.replay()

        vocabulary = vocfactory(context)
        self.assertEqual(sorted(self._get_term_titles_from_vocabulary(vocabulary)),
                         [u'20', u'30'])

    def test_validator(self):
        request = self.mocker.mock()
        self.expect(request.get('PATH_INFO', ANY)).result('somepath/++add++type')

        field = lifecycle.ILifeCycle['custody_period']

        context = None
        view = None
        widget = None

        self.replay()

        validator = getMultiAdapter((context, request, view, field, widget), IValidator)
        validator.validate(20)

        with TestCase.assertRaises(self, ConstraintNotSatisfied):
            validator.validate(15)

    def test_validator_in_context(self):
        request = self.mocker.mock()
        self.expect(request.get('PATH_INFO', ANY)).result(
            'somepath/++add++type').count(0, None)

        context = self.mocker.mock()
        self.expect(context.REQUEST).result(request).count(0, None)
        self.expect(context.custody_period).result(20).count(0, None)
        self.expect(context.aq_inner).result(context).count(0, None)
        self.expect(context.aq_parent).result(None).count(0, None)

        field = lifecycle.ILifeCycle['custody_period']

        view = None
        widget = None

        self.replay()

        validator = getMultiAdapter((context, request, view, field, widget), IValidator)
        validator.validate(20)
        validator.validate(30)

        with TestCase.assertRaises(self, ConstraintNotSatisfied):
            validator.validate(10)

    def test_default_value(self):
        field = lifecycle.ILifeCycle['custody_period']

        portal = self.create_dummy()
        directlyProvides(portal, ISiteRoot)

        default_value = getMultiAdapter(
            (portal,  # context
             None,  # request
             None,  # form
             field,  # field
             None,  # Widget
             ),
            IValue,
            name='default')
        self.assertEqual(default_value.get(), 30)

    def test_default_value_in_context(self):
        field = lifecycle.ILifeCycle['custody_period']

        context = self.create_dummy(custody_period=10)
        directlyProvides(context, lifecycle.ILifeCycle)

        default_value = getMultiAdapter(
            (context,  # context
             None,  # request
             None,  # form
             field,  # field
             None,  # Widget
             ),
            IValue,
            name='default')
        self.assertEqual(default_value.get(), 10)
