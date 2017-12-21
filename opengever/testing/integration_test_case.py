from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from ftw.flamegraph import flamegraph
from ftw.mail.mail import IMail
from functools import wraps
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.journal.tests.utils import get_journal_entry
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.model.agendaitem import AgendaItem
from opengever.meeting.wrapper import MeetingWrapper
from opengever.ogds.base.utils import ogds_service
from opengever.task.task import ITask
from operator import methodcaller
from plone import api
from plone.app.relationfield.event import update_behavior_relations
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.namedfile.file import NamedBlobFile
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from sqlalchemy.sql.expression import desc
from unittest import TestCase
from z3c.relationfield.relation import RelationValue
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.intid.interfaces import IIntIds
import timeit


FEATURE_FLAGS = {
    'meeting': 'opengever.meeting.interfaces.IMeetingSettings.is_feature_enabled',
    'word-meeting': 'opengever.meeting.interfaces.IMeetingSettings.is_word_implementation_enabled',
    'dossiertemplate': ('opengever.dossier.dossiertemplate'
                        '.interfaces.IDossierTemplateSettings.is_feature_enabled'),
    'ech0147-export': 'opengever.ech0147.interfaces.IECH0147Settings.ech0147_export_enabled',
    'ech0147-import': 'opengever.ech0147.interfaces.IECH0147Settings.ech0147_import_enabled',
    'extjs': 'ftw.tabbedview.interfaces.ITabbedView.extjs_enabled',
    'bumblebee': 'opengever.bumblebee.interfaces.IGeverBumblebeeSettings.is_feature_enabled',
    'bumblebee-open-pdf-new-tab': 'opengever.bumblebee.interfaces.IGeverBumblebeeSettings.open_pdf_in_a_new_window',
    'activity': 'opengever.activity.interfaces.IActivitySettings.is_feature_enabled',
    'contact': 'opengever.contact.interfaces.IContactSettings.is_feature_enabled',
    'doc-properties': 'opengever.dossier.interfaces.ITemplateFolderProperties.create_doc_properties'
}

FEATURE_PROFILES = {
    'filing_number': 'opengever.dossier:filing',
}


class IntegrationTestCase(TestCase):
    layer = OPENGEVER_INTEGRATION_TESTING
    features = ()

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.deactivate_extjs()
        map(self.activate_feature, self.features)

    @staticmethod
    def open_flamegraph(func):
        """Test decorator for opening a flamegraph for creating a flamegraph of
        the decorated test and opening it in the default browser using OS X's
        "open" command.

        Example:

        @IntegrationTestCase.open_flamegraph
        def test_critical_feature(self):
            pass

        """
        return flamegraph(open_svg=True)(func)

    @staticmethod
    def clock(func):
        """Decorator for measuring the duration of a test and printing the result.
        This function is meant to be used temporarily in development.

        Example:
        @IntegrationTestCase.clock
        def test_something(self):
            pass
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            timer = timeit.default_timer
            start = timer()
            try:
                return func(self, *args, **kwargs)
            finally:
                end = timer()
                print ''
                print '{}.{} took {:.3f} ms'.format(
                    type(self).__name__,
                    func.__name__,
                    (end - start) * 1000)
        return wrapper

    def login(self, user, browser=None):
        """Login a user by passing in the user object.
        Common users are available through the USER_LOOKUP_TABLE.

        Log in security manager and browser:
        >>> self.login(self.dossier_responsible, browser)
        Log in only security manager:
        >>> self.login(self.dossier_responsible)

        The method may also be used used as context manager, ensuring that
        after leaving the same user is logged in as before.
        """

        if hasattr(user, 'getId'):
            userid = user.getId()
        else:
            userid = user

        security_manager = getSecurityManager()
        if userid == SITE_OWNER_NAME:
            login(self.layer['app'], userid)
        else:
            login(self.portal, userid)

        if browser is not None:
            browser_auth_headers = filter(
                lambda item: item[0] == 'Authorization',
                browser.session_headers)
            browser.login(userid)

        @contextmanager
        def login_context_manager():
            try:
                yield
            finally:
                setSecurityManager(security_manager)
                if browser is not None:
                    browser.clear_request_header('Authorization')
                    [browser.append_request_header(name, value)
                     for (name, value) in browser_auth_headers]

        return login_context_manager()

    def deactivate_extjs(self):
        """ExtJS is JavaScript and therefore currently untestable with
        ftw.testbrowser.
        In order to test listing tabs, we disable ExtJS in tests by default.
        It can be reactivated by activating the fature "extjs":

        >>> self.activate_feature('extjs')
        """
        api.portal.set_registry_record(
            'ftw.tabbedview.interfaces.ITabbedView.extjs_enabled', False)

    def activate_feature(self, feature):
        """Activate a feature flag.
        """
        if feature in FEATURE_FLAGS:
            api.portal.set_registry_record(FEATURE_FLAGS[feature], True)
        elif feature in FEATURE_PROFILES:
            applyProfile(self.portal, FEATURE_PROFILES[feature])
        else:
            raise ValueError('Invalid {!r}'.format(feature))

    def deactivate_feature(self, feature):
        """Deactivate a feature flag.
        """
        if feature in FEATURE_FLAGS:
            api.portal.set_registry_record(FEATURE_FLAGS[feature], False)
        elif feature in FEATURE_PROFILES:
            raise NotImplementedError('Feel free to implement.')
        else:
            raise ValueError('Invalid {!r}'.format(feature))

    def __getattr__(self, name):
        """Make it possible to access objects from the content lookup table
        directly with attribute access on the test case.
        """
        obj = self._lookup_from_table(name)
        if obj is not None:
            return obj
        else:
            return self.__getattribute__(name)

    @property
    def dossier_tasks(self):
        """All tasks within self.dossier.
        """
        return map(self.brain_to_object,
                   api.content.find(self.dossier, object_provides=ITask))

    def _lookup_from_table(self, name):
        """This method helps to look up persistent objects or user objects which
        were created in the fixture and registered there with a name.
        """
        try:
            table = self.layer['fixture_lookup_table']
        except KeyError:
            # The layer has not yet set up the fixture.
            return None
        if name not in table:
            return None

        type_, value = table[name]
        if type_ == 'object':
            locals()['__traceback_info__'] = {
                'path': value,
                'current user': getSecurityManager().getUser()}
            return self.portal.restrictedTraverse(value)

        elif type_ == 'user':
            return api.user.get(value)

        elif type_ == 'raw':
            return value

        else:
            raise ValueError('Unsupport lookup entry type {!r}'.format(type_))

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

    def get_catalog_indexdata(self, obj):
        """Return the catalog index data for an object as dict.
        """
        catalog = api.portal.get_tool('portal_catalog')
        rid = catalog.getrid('/'.join(obj.getPhysicalPath()))
        return catalog.getIndexDataForRID(rid)

    def assert_index_value(self, expected_value, index_name, *objects):
        """Asserts that an index exists and has a specific value for a
        given object.
        """
        for obj in objects:
            index_data = self.get_catalog_indexdata(obj)
            self.assertIn(
                index_name, index_data,
                'Index {!r} does not exist.'.format(index_name))
            self.assertEquals(
                expected_value, index_data[index_name],
                'Unexpected index value {!r} in index {!r} for {!r}'.format(
                    index_data[index_name], index_name, obj))

    def get_catalog_metadata(self, obj):
        """Return the catalog metadata for an object as dict.
        """
        catalog = api.portal.get_tool('portal_catalog')
        rid = catalog.getrid('/'.join(obj.getPhysicalPath()))
        return catalog.getMetadataForRID(rid)

    def assert_metadata_value(self, expected_value, metadata_name, *objects):
        """Asserts that an metadata exists and has a specific value for a
        given object.
        """
        for obj in objects:
            metadata = self.get_catalog_metadata(obj)
            self.assertIn(
                metadata_name, metadata,
                'Metadata {!r} does not exist.'.format(metadata_name))
            self.assertEquals(
                expected_value, metadata[metadata_name],
                'Unexpected metadata value {!r} in metadata {!r} for {!r}'.format(
                    metadata[metadata_name], metadata_name, obj))

    def assert_index_and_metadata(self, expected_value, name, *objects):
        """Assert that an index and a metadata with the same name both exist
        and have the same value for a given object.
        """
        self.assert_index_value(expected_value, name, *objects)
        self.assert_metadata_value(expected_value, name, *objects)

    def set_workflow_state(self, new_workflow_state_id, *objects):
        """Set the workflow state of one or many objects.
        When the state is changed for multiple nested objects at once, the
        method can optimize reindexing security so that it is not executed
        multiple times for the same object.
        """
        wftool = api.portal.get_tool('portal_workflow')

        for obj in objects:
            chain = wftool.getChainFor(obj)
            self.assertEquals(
                1, len(chain),
                'set_workflow_state does only support objects with'
                ' exactly one workflow, but {!r} has {!r}.'.format(obj, chain))
            workflow = wftool[chain[0]]
            self.assertIn(new_workflow_state_id, workflow.states)

            wftool.setStatusOf(chain[0], obj, {
                'review_state': new_workflow_state_id,
                'action': '',
                'actor': ''})
            workflow.updateRoleMappingsFor(obj)
            obj.reindexObject(idxs=['review_state'])

            if ITask.providedBy(obj):
                obj.get_sql_object().review_state = new_workflow_state_id

        # reindexObjectSecurity is recursive. We should avoid updating the same
        # object twice when the parent is changed too.
        security_reindexed = []
        for obj in sorted(objects, key=methodcaller('getPhysicalPath')):
            current_path = '/'.join(obj.getPhysicalPath())
            if any(filter(lambda path: current_path.startswith(path),
                          security_reindexed)):
                # We just have updated the security of a parent recursively,
                # thus the security of ``obj`` must be up to date at this point.
                break

            obj.reindexObjectSecurity()
            security_reindexed.append(current_path)

    def assert_workflow_state(self, workflow_state_id, obj):
        """Assert the workflow state of an object and of its brain.
        """

        expected = {
            'object': workflow_state_id,
            'catalog index': workflow_state_id,
            'catalog metadata': workflow_state_id}

        got = {
            'object': api.content.get_state(obj),
            'catalog index': self.get_catalog_indexdata(obj)['review_state'],
            'catalog metadata': self.get_catalog_metadata(obj)['review_state']}

        self.assertEqual(
            expected, got,
            'Object {!r} has an incorrect workflow state.'.format(obj))

    def assert_has_permissions(self, permissions, obj, msg=None):
        """Assert that the current user has all given permissions on the context.
        """
        missing_permissions = [
            permission for permission in permissions
            if not api.user.has_permission(permission, obj=obj)]
        self.assertEquals(
            [], missing_permissions,
            'Missing permissions for user {!r} on {!r}. {}'.format(
                api.user.get_current(),
                obj,
                msg or ''))

    def assert_has_not_permissions(self, permissions, obj, msg=None):
        """Assert that the current user has none of the given permissions
        on the context.
        """
        present_permissions = [
            permission for permission in permissions
            if api.user.has_permission(permission, obj=obj)]
        self.assertEquals(
            [], present_permissions,
            'Too many permissions for user {!r} on {!r}. {}'.format(
                api.user.get_current(),
                obj,
                msg or ''))

    def assert_journal_entry(self, obj, action_type, title, comment=None, entry=-1):  # noqa
        entry = get_journal_entry(obj, entry)
        action = entry.get('action')

        self.assertEquals(action_type, action.get('type'))
        self.assertEquals(title, translate(action.get('title')))

        if comment is not None:
            self.assertEquals(comment, entry.get('comments'))

    def assert_local_roles(self, expected_roles, user, context):
        if hasattr(user, 'getId'):
            userid = user.getId()
        else:
            userid = user
        current_roles = dict(context.get_local_roles()).get(userid, [])
        self.assertItemsEqual(
            expected_roles, current_roles,
            "The user '{}' should have the roles {!r} on context {!r}. "
            "But he has {}".format(userid, expected_roles, context, current_roles))

    def assert_submitted_document_created(self, proposal, document,
                                       submitted_version=0):
        portal = api.portal.get()
        submitted_document_model = SubmittedDocument.query.get_by_source(
            proposal,
            document,
            )

        submitted_document = portal.restrictedTraverse(
            submitted_document_model.submitted_physical_path.encode('utf-8'),
            )

        self.assertIsNotNone(submitted_document_model)

        self.assertEqual(
            Oguid.for_object(submitted_document),
            submitted_document_model.submitted_oguid,
            )

        self.assertEqual(
            submitted_version,
            submitted_document_model.submitted_version,
            )

        self.assertEqual(
            proposal.load_model(),
            submitted_document_model.proposal,
            )

    def brain_to_object(self, brain):
        """Return the object of a brain.
        """
        return brain.getObject()

    def object_to_brain(self, obj):
        """Return the brain of an object.
        Make sure that the current user is allowed to view the object.
        """
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(path={'query': '/'.join(obj.getPhysicalPath()),
                               'depth': 0})
        self.assertEquals(1, len(brains))
        return brains[0]

    def enable_languages(self):
        """Enable a multi-language configuration with German and French.
        """
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.use_combined_language_codes = True
        lang_tool.addSupportedLanguage('de-ch')
        lang_tool.addSupportedLanguage('fr-ch')
        lang_tool.addSupportedLanguage('en')

    def set_related_items(self, obj, items, fieldname='relatedItems',
                          append=False):
        """Set the related items on an object and update the relation catalog.
        """
        assert isinstance(items, (list, tuple)), 'items must be list or tuple'
        if append:
            relations = getattr(obj, fieldname, [])
        else:
            relations = []

        intids = map(getUtility(IIntIds).getId, items)
        relations += map(RelationValue, intids)
        setattr(obj, fieldname, relations)
        update_behavior_relations(obj, None)

    def add_related_item(self, obj, related_obj, fieldname='relatedItems'):
        """Add a relation from obj to related_obj.
        """
        self.set_related_items(obj, [related_obj], fieldname=fieldname,
                               append=True)

    def checkout_document(self, document):
        """Checkout the given document.
        """
        return self.get_checkout_manager(document).checkout()

    def get_checkout_manager(self, document):
        """Returns the checkin checkout manager for a document.
        """
        return getMultiAdapter((document, document.REQUEST),
                               ICheckinCheckoutManager)

    def schedule_proposal(self, meeting, submitted_proposal):
        """Meeting: schedule a proposal for a meeting and return the
        agenda item.
        """
        if isinstance(meeting, MeetingWrapper):
            meeting = meeting.model

        proposal_model = submitted_proposal.load_model()
        meeting.schedule_proposal(proposal_model)
        self.assertEquals(proposal_model.STATE_SCHEDULED,
                          proposal_model.get_state())
        agenda_item = AgendaItem.query.order_by(desc('id')).first()
        return agenda_item

    def schedule_ad_hoc(self, meeting, title):
        if isinstance(meeting, MeetingWrapper):
            meeting = meeting.model

        meeting.schedule_ad_hoc(title)
        agenda_item = AgendaItem.query.order_by(desc('id')).first()
        return agenda_item

    def schedule_paragraph(self, meeting, title):
        if isinstance(meeting, MeetingWrapper):
            meeting = meeting.model

        meeting.schedule_text(title, is_paragraph=True)
        agenda_item = AgendaItem.query.order_by(desc('id')).first()
        return agenda_item

    def as_relation_value(self, obj):
        return RelationValue(getUtility(IIntIds).getId(obj))

    def assert_portlet_inheritance_blocked(self, manager_name, obj):
        manager = getUtility(
            IPortletManager, name=manager_name, context=obj)
        assignable = getMultiAdapter(
            (obj, manager), ILocalPortletAssignmentManager)
        self.assertTrue(assignable.getBlacklistStatus(CONTEXT_CATEGORY))

    def change_mail_data(self, mail, data):
        old_file = IMail(self.mail).message
        IMail(self.mail).message = NamedBlobFile(
            data=data, filename=old_file.filename)

    def agenda_item_url(self, agenda_item, endpoint):
        return '{}/agenda_items/{}/{}'.format(
            agenda_item.meeting.get_url(view=None),
            agenda_item.agenda_item_id,
            endpoint)

    def get_ogds_user(self, user):
        return ogds_service().fetch_user(user.getId())
