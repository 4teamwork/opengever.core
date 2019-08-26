from datetime import datetime
from ftw.testing import freeze
from opengever.base.response import AutoResponseChangesTracker
from opengever.base.response import IChangesTracker
from opengever.base.response import IResponseContainer
from opengever.base.response import NullChangesTracker
from opengever.base.response import Response
from opengever.base.response import ResponseContainer
from opengever.testing import IntegrationTestCase
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter


class TestResponse(IntegrationTestCase):

    def test_creator_is_current_user(self):
        self.login(self.workspace_member)
        response = Response('Bitte weiter abklaeren.')

        self.assertEqual(self.workspace_member.id, response.creator)

    def test_created_is_datetime_now(self):
        self.login(self.workspace_member)
        with freeze(datetime(2016, 12, 9, 9, 40)):
            response = Response('Bitte weiter abklaeren.')

        self.assertEqual(datetime(2016, 12, 9, 9, 40), response.created)


class TestResponseContainer(IntegrationTestCase):

    def test_stores_response_in_the_annotations(self):
        self.login(self.workspace_member)

        annotations = IAnnotations(self.todo)
        self.assertNotIn(ResponseContainer.ANNOTATION_KEY, annotations.keys())

        response = Response('Bitte weiter abklaeren.')
        container = IResponseContainer(self.todo)
        container.add(response)

        storage = annotations[ResponseContainer.ANNOTATION_KEY]
        self.assertEqual([response], list(storage.values()))

    def test_add_expects_response_objects(self):
        self.login(self.workspace_member)

        annotations = IAnnotations(self.todo)
        self.assertNotIn(ResponseContainer.ANNOTATION_KEY, annotations.keys())

        container = IResponseContainer(self.todo)
        with self.assertRaises(ValueError):
            container.add(object())

        storage = annotations[ResponseContainer.ANNOTATION_KEY]
        self.assertEqual([], list(storage.keys()))

    def test_list_returns_response_in_add_order(self):
        self.login(self.workspace_member)
        IResponseContainer(self.todo).list()

        container = IResponseContainer(self.todo)

        responses = [Response('2.'), Response('3.'), Response('1.')]
        [container.add(response) for response in responses]
        self.assertEqual(responses, container.list())

    def test_list_does_not_initalize_the_annotation_list(self):
        self.login(self.workspace_member)
        self.assertEqual([], IResponseContainer(self.todo).list())
        self.assertNotIn(
            ResponseContainer.ANNOTATION_KEY, IAnnotations(self.todo).keys())


class TestNullChangesTracker(IntegrationTestCase):
    def test_do_not_fail_as_a_contextmanager(self):
        self.login(self.regular_user)
        changes_tracker = getMultiAdapter((self.dossier, self.request), IChangesTracker)

        with changes_tracker.track_changes(['title']):
            self.dossier.title = 'after'

    def test_is_default_adapter(self):
        self.login(self.regular_user)
        changes_tracker = getMultiAdapter((self.dossier, self.request), IChangesTracker)

        self.assertIsInstance(changes_tracker, NullChangesTracker)


class TestAutoResponseChangesTracker(IntegrationTestCase):
    def test_adapter_for_IResponseSupported_objects(self):
        self.login(self.workspace_member)
        changes_tracker = getMultiAdapter((self.todo, self.request), IChangesTracker)

        self.assertIsInstance(changes_tracker, AutoResponseChangesTracker)

    def test_tracks_changes_of_an_object(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'
        changes_tracker = getMultiAdapter((self.todo, self.request), IChangesTracker)
        with changes_tracker.track_changes(['title']):
            self.todo.title = u'James B\xc3\xb6nd'

        self.assertDictEqual({'title': (u'before', u'James B\xc3\xb6nd')}, changes_tracker.changes)

    def test_track_multiple_fields(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'
        self.todo.responsible = self.workspace_member.getId()
        changes_tracker = getMultiAdapter((self.todo, self.request), IChangesTracker)
        with changes_tracker.track_changes(['title', 'responsible']):
            self.todo.title = u'after'
            self.todo.responsible = self.workspace_admin.getId()

        self.assertDictEqual(
            {
                'title': (u'before', u'after'),
                'responsible': (
                    {u'token': u'beatrice.schrodinger', u'title': u'Schr\xf6dinger B\xe9atrice'},
                    {u'token': u'fridolin.hugentobler', u'title': u'Hugentobler Fridolin'},
                )
            },
            changes_tracker.changes)

    def test_do_not_track_not_changed_fields(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'

        changes_tracker = getMultiAdapter((self.todo, self.request), IChangesTracker)
        with changes_tracker.track_changes(['title']):
            self.todo.title = u'before'

        self.assertDictEqual({}, changes_tracker.changes)

    def test_do_not_track_not_tracking_fields(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'

        changes_tracker = getMultiAdapter((self.todo, self.request), IChangesTracker)
        with changes_tracker.track_changes(['responsible']):
            self.todo.title = u'after'

        self.assertDictEqual({}, changes_tracker.changes)

    def test_create_a_response_object_with_all_changes(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'
        self.todo.responsible = self.workspace_member.getId()

        changes_tracker = getMultiAdapter((self.todo, self.request), IChangesTracker)
        with changes_tracker.track_changes(['title', 'responsible']):
            self.todo.title = u'after'
            self.todo.responsible = self.workspace_admin.getId()

        self.assertItemsEqual(
            [
                {
                    'field_id': 'responsible',
                    'before': {u'token': u'beatrice.schrodinger', u'title': u'Schr\xf6dinger B\xe9atrice'},
                    'after': {u'token': u'fridolin.hugentobler', u'title': u'Hugentobler Fridolin'}
                },
                {
                    'field_id': 'title',
                    'before': 'before',
                    'after': 'after'
                }
            ],
            IResponseContainer(self.todo).list()[0].changes)

    def test_do_not_create_a_response_object_if_there_are_no_changes(self):
        self.login(self.workspace_member)

        changes_tracker = getMultiAdapter((self.todo, self.request), IChangesTracker)
        with changes_tracker.track_changes(['title']):
            pass

        self.assertEqual([], IResponseContainer(self.todo).list())
