from datetime import datetime
from ftw.testing import freeze
from opengever.base.response import AutoResponseChangesTracker
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.base.response import ResponseContainer
from opengever.testing import IntegrationTestCase
from zope.annotation import IAnnotations


class TestResponse(IntegrationTestCase):

    def test_creator_is_current_user(self):
        self.login(self.workspace_member)
        response = Response()

        self.assertEqual(self.workspace_member.id, response.creator)

    def test_created_is_datetime_now(self):
        self.login(self.workspace_member)
        with freeze(datetime(2016, 12, 9, 9, 40)):
            response = Response()

        self.assertEqual(datetime(2016, 12, 9, 9, 40), response.created)


class TestResponseContainer(IntegrationTestCase):

    def test_stores_response_in_the_annotations(self):
        self.login(self.workspace_member)

        annotations = IAnnotations(self.todo)

        response = Response()
        container = IResponseContainer(self.todo)
        container.add(response)

        storage = annotations[ResponseContainer.ANNOTATION_KEY]
        self.assertEqual(response, list(storage.values())[-1])

    def test_add_expects_response_objects(self):
        self.login(self.workspace_member)

        self.assertEqual(1, len(IResponseContainer(self.todo).list()))

        container = IResponseContainer(self.todo)
        with self.assertRaises(ValueError):
            container.add(object())

        self.assertEqual(1, len(IResponseContainer(self.todo).list()))

    def test_list_returns_response_in_add_order__(self):
        self.login(self.workspace_member)

        container = IResponseContainer(self.todo)

        responses = [Response(), Response(), Response()]
        [container.add(response) for response in responses]
        self.assertEqual(responses, container.list()[1:])

    def test_list_does_not_initalize_the_annotation_list(self):
        self.login(self.workspace_member)
        del IAnnotations(self.todo)[ResponseContainer.ANNOTATION_KEY]
        self.assertEqual([], IResponseContainer(self.todo).list())
        self.assertNotIn(
            ResponseContainer.ANNOTATION_KEY, IAnnotations(self.todo).keys())


class TestAutoResponseChangesTracker(IntegrationTestCase):
    def test_adapter_for_IResponseSupported_objects(self):
        self.login(self.workspace_member)
        changes_tracker = AutoResponseChangesTracker(self.todo, self.request)

        self.assertIsInstance(changes_tracker, AutoResponseChangesTracker)

    def test_tracks_changes_of_an_object(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'
        changes_tracker = AutoResponseChangesTracker(self.todo, self.request)
        with changes_tracker.track_changes(['title']):
            self.todo.title = u'James B\xc3\xb6nd'

        self.assertDictEqual({'title': (u'before', u'James B\xc3\xb6nd')}, changes_tracker.changes)

    def test_track_multiple_fields(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'
        self.todo.responsible = self.workspace_member.getId()
        changes_tracker = AutoResponseChangesTracker(self.todo, self.request)
        with changes_tracker.track_changes(['title', 'responsible']):
            self.todo.title = u'after'
            self.todo.responsible = self.workspace_admin.getId()

        self.assertDictEqual(
            {
                'title': (u'before', u'after'),
                'responsible': (
                    {u'token': u'beatrice.schrodinger',
                     u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)'},
                    {u'token': u'fridolin.hugentobler',
                     u'title': u'Hugentobler Fridolin (fridolin.hugentobler)'},
                )
            },
            changes_tracker.changes)

    def test_do_not_track_not_changed_fields(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'

        changes_tracker = AutoResponseChangesTracker(self.todo, self.request)
        with changes_tracker.track_changes(['title']):
            self.todo.title = u'before'

        self.assertDictEqual({}, changes_tracker.changes)

    def test_do_not_track_not_tracking_fields(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'

        changes_tracker = AutoResponseChangesTracker(self.todo, self.request)
        with changes_tracker.track_changes(['responsible']):
            self.todo.title = u'after'

        self.assertDictEqual({}, changes_tracker.changes)

    def test_create_a_response_object_with_all_changes(self):
        self.login(self.workspace_member)
        self.todo.title = u'before'
        self.todo.responsible = self.workspace_member.getId()

        changes_tracker = AutoResponseChangesTracker(self.todo, self.request)
        with changes_tracker.track_changes(['title', 'responsible']):
            self.todo.title = u'after'
            self.todo.responsible = self.workspace_admin.getId()

        self.assertItemsEqual(
            [
                {
                    'field_id': 'responsible',
                    'before': {u'token': u'beatrice.schrodinger',
                               u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)'},
                    'after': {u'token': u'fridolin.hugentobler',
                              u'title': u'Hugentobler Fridolin (fridolin.hugentobler)'},
                    'field_title': '',
                },
                {
                    'field_id': 'title',
                    'before': 'before',
                    'after': 'after',
                    'field_title': '',
                }
            ],
            IResponseContainer(self.todo).list()[-1].changes)

    def test_do_not_create_a_response_object_if_there_are_no_changes(self):
        self.login(self.workspace_member)

        self.assertEqual(1, len(IResponseContainer(self.todo).list()))

        changes_tracker = AutoResponseChangesTracker(self.todo, self.request)
        with changes_tracker.track_changes(['title']):
            pass

        self.assertEqual(1, len(IResponseContainer(self.todo).list()))
