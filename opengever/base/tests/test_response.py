from datetime import datetime
from zope.annotation import IAnnotations
from ftw.testing import freeze
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.base.response import ResponseContainer
from opengever.testing import IntegrationTestCase


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

        self.assertEqual([response],
                         annotations[ResponseContainer.ANNOTATION_KEY])

    def test_add_expects_response_objects(self):
        self.login(self.workspace_member)

        annotations = IAnnotations(self.todo)
        self.assertNotIn(ResponseContainer.ANNOTATION_KEY, annotations.keys())

        response = Response('Bitte weiter abklaeren.')
        container = IResponseContainer(self.todo)
        container.add(response)

        self.assertEqual([response],
                         annotations[ResponseContainer.ANNOTATION_KEY])

    def test_list_returns_response_in_add_order(self):
        self.login(self.workspace_member)
        IResponseContainer(self.todo).list()

        container = IResponseContainer(self.todo)

        responses = [Response('1.'), Response('2.'), Response('3.')]
        [container.add(response) for response in responses]
        self.assertEqual(responses, container.list())

    def test_list_does_not_initalize_the_annotation_list(self):
        self.login(self.workspace_member)
        self.assertEqual([], IResponseContainer(self.todo).list())
        self.assertNotIn(
            ResponseContainer.ANNOTATION_KEY, IAnnotations(self.todo).keys())
