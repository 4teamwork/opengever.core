from AccessControl import getSecurityManager
from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.keywordwidget.tests import widget  # keep!
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.journal.tests.utils import get_journal_entry
from opengever.meeting.model import SubmittedDocument
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User
from opengever.testing import builders  # keep!
from opengever.testing.helpers import localized_datetime
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import alsoProvides
import json
import transaction
import unittest


# Squelch pyflakes about unused exports
widget
builders


class TestCase(unittest.TestCase):
    """Provide a shared base for opengever.core test classes."""

    def assertSubmittedDocumentCreated(self, proposal, doc_or_mail, submitted_version=0):
        submitted_document_model = SubmittedDocument.query.get_by_source(
            proposal, doc_or_mail)
        self.assertIsNotNone(submitted_document_model)
        portal = api.portal.get()
        submitted_document = portal.restrictedTraverse(
            submitted_document_model.submitted_physical_path.encode('utf-8'))
        self.assertEqual(Oguid.for_object(submitted_document),
                         submitted_document_model.submitted_oguid)
        self.assertEqual(submitted_version,
                         submitted_document_model.submitted_version)
        self.assertEqual(proposal.load_model(),
                         submitted_document_model.proposal)

    @contextmanager
    def observe_children(self, obj, check_security=True):
        """Observe the children of an object for testing that children were
        added or removed within the context manager.
        """
        if check_security:
            def allowed(obj):
                return getSecurityManager().checkPermission(
                    'Access contents information', obj)
        else:
            def allowed(obj):
                return True

        children = {'before': filter(allowed, obj.objectValues())}
        yield children
        children['after'] = filter(allowed, obj.objectValues())
        children['added'] = set(children['after']) - set(children['before'])
        children['removed'] = set(children['before']) - set(children['after'])


class FunctionalTestCase(TestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING
    use_default_fixture = True

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.app.REQUEST
        alsoProvides(self.request, IOpengeverBaseLayer)
        self.membership_tool = getToolByName(self.portal, 'portal_membership')

        if self.use_default_fixture:
            user, org_unit, admin_unit = create(
                Builder('fixture').with_all_unit_setup())

            # Used in the properties below to facilitate lazy access
            self._user_id = user.userid
            self._org_unit_id = org_unit.unit_id
            self._admin_unit_id = admin_unit.unit_id

        self.grant('Contributor', 'Editor', 'Reader')

        # necessary to force tabbed-view into HTML mode, because
        # ftw.testbrowser does not support JavaScript.
        api.portal.set_registry_record(
            'ftw.tabbedview.interfaces.ITabbedView.extjs_enabled', False)

        # currently necessary to have persistent SQL data
        transaction.commit()

    """
    These properties enforce lazy access to mapped objects, in oder to avoid
    keeping around objects from an expired session when the transaction is
    committed. That way we make sure to always get a fresh object
    when a test case uses self.user, self.org_unit etc...
    """

    def localized_datetime(self, *args, **kwargs):
        return localized_datetime(*args, **kwargs)

    def get_user(self):
        return User.get(self._user_id)

    def set_user(self, value):
        self._user_id = value.userid

    user = property(get_user, set_user)

    def get_org_unit(self):
        return OrgUnit.get(self._org_unit_id)

    def set_org_unit(self, value):
        self._org_unit_id = value.unit_id

    org_unit = property(get_org_unit, set_org_unit)

    def get_admin_unit(self):
        return AdminUnit.get(self._admin_unit_id)

    def set_admin_unit(self, value):
        self._admin_unit_id = value.unit_id

    admin_unit = property(get_admin_unit, set_admin_unit)

    def setup_fullname(self, user_id=TEST_USER_ID, fullname=None):
        member = self.membership_tool.getMemberById(user_id)
        member.setProperties(fullname=fullname)
        transaction.commit()

    def set_docproperty_export_enabled(self, enabled=True):
        registry = getUtility(IRegistry)
        props = registry.forInterface(ITemplateFolderProperties)
        props.create_doc_properties = enabled

    def grant(self, *roles, **kwargs):
        user_id = kwargs.get('user_id', TEST_USER_ID)
        context = kwargs.get('on', None)

        if context is None:
            setRoles(self.portal, user_id, list(roles))
        else:
            RoleAssignmentManager(context).add_or_update_assignment(
                SharingRoleAssignment(user_id, list(roles)))

        transaction.commit()

    def login(self, user_id=TEST_USER_NAME):
        login(self.portal, user_id)
        return self.membership_tool.getAuthenticatedMember()

    def prepareSession(self):
        if 'SESSION' not in self.request.keys():
            self.request.SESSION = {}

    def assertProvides(self, obj, interface=None):
        self.assertTrue(interface.providedBy(obj),
                        "%s should provide %s" % (obj, interface))

    def brains_to_objects(self, brains):
        return [each.getObject() for each in brains]

    """
    Vocabulary assert helpers
    """

    def assertTerms(self, expected_terms, vocabulary):
        effective_terms = []
        for term in list(vocabulary):
            effective_terms.append((term.value, term.title))

        self.assertEquals(expected_terms, effective_terms)

    def assertTermKeys(self, keys, vocabulary):
        terms = [term.value for term in vocabulary]
        keys.sort()
        terms.sort()
        self.assertEquals(keys, terms)

    def assertInTerms(self, value, vocabulary):
        self.assertIn(value, [term.value for term in vocabulary])

    def assertNotInTerms(self, value, vocabulary):
        self.assertNotIn(value, [term.value for term in vocabulary])

    """
    Journal assert helpers
    """

    def assert_journal_entry(self, obj, action_type, title, entry=-1):
        entry = get_journal_entry(obj, entry)
        action = entry.get('action')
        self.assertEquals(action_type, action.get('type'))
        self.assertEquals(title, translate(action.get('title')))

    """
    Browser API
    Deprecated, please don't extend this API and use
    opengever.testing.browser whenever possible.
    """

    def assertResponseStatus(self, code):
        self.assertEquals(code, self.portal.REQUEST.response.status)

    def assertResponseHeader(self, name, value):
        self.assertEquals(value, self.portal.REQUEST.response.headers.get(name))

    def assert_json_equal(self, expected, got, msg=None):
        pretty = {'sort_keys': True, 'indent': 4, 'separators': (',', ': ')}
        expected_json = json.dumps(expected, **pretty)
        got_json = json.dumps(got, **pretty)
        self.maxDiff = None
        self.assertMultiLineEqual(expected_json, got_json, msg)

    def assert_portlet_inheritance_blocked(self, manager_name, obj):
        manager = getUtility(
            IPortletManager, name=manager_name, context=obj)
        assignable = getMultiAdapter(
            (obj, manager), ILocalPortletAssignmentManager)
        self.assertTrue(assignable.getBlacklistStatus(CONTEXT_CATEGORY))
