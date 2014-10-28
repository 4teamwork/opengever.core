from ftw.builder import Builder
from ftw.builder import create
from lxml.cssselect import css_to_xpath
from lxml.etree import fromstring
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskLinkGeneration(FunctionalTestCase):

    def setUp(self):
        super(TestTaskLinkGeneration, self).setUp()

        additional_admin_unit = create(Builder('admin_unit').id(u'additional'))
        create(Builder('org_unit').id(u'additional')
               .having(admin_unit=additional_admin_unit))

    def add_task(self, **kwargs):
        attr = {
            'title': u'Do it!',
            'physical_path': "qux/dossier-1/task-2",
            'assigned_org_unit': 'client1',
            'issuing_org_unit': 'client1',
            'review_state': 'task-state-tested-and-closed',
            'responsible': TEST_USER_ID,
            'admin_unit_id': 'client1',
            'breadcrumb_title': '0 Allgemeines > 01 SonstigesTestdossier 4tw > Testaufgabe',
            'principals': [TEST_USER_ID]}
        attr.update(**kwargs)

        task = create(Builder('globalindex_task').having(**attr))
        return task

    def add_task_and_get_link(self, **kwargs):
        task = self.add_task(**kwargs)
        return fromstring(task.get_link())

    def test_task_is_linked_when_user_has_access(self):
        link = self.add_task_and_get_link()
        link_tag = link.xpath(css_to_xpath('a'))[0]

        self.assertEquals(
            'http://example.com/qux/dossier-1/task-2',
            link_tag.get('href'))

    def test_task_is_not_linked_when_user_has_no_access(self):
        link = self.add_task_and_get_link(principals=[])
        self.assertEquals([], link.xpath(css_to_xpath('a')))

        # check that all the other parts are the same
        self.assertEquals('wf-task-state-tested-and-closed',
                          link.xpath(css_to_xpath('span'))[0].get('class'))
        self.assertEquals('Do it!',
                          link.xpath(css_to_xpath('span'))[1].text)
        self.assertEquals('(Client1 / Test User (test_user_1_))',
                          link.xpath(css_to_xpath('span'))[2].text)

    def test_link_title_is_breadcrumb(self):
        link = self.add_task_and_get_link()
        link_tag = link.xpath(css_to_xpath('a'))[0]

        self.assertEquals(
            '[Client1] > 0 Allgemeines > 01 SonstigesTestdossier 4tw > Testaufgabe',
            link_tag.get('title'))

    def test_link_text_is_task_title(self):
        link = self.add_task_and_get_link()
        span_tag = link.xpath(css_to_xpath('a span'))[0]

        self.assertEquals('Do it!', span_tag.text)

    def test_link_contains_contenttype_class(self):
        link = self.add_task_and_get_link()
        span_tag = link.xpath(css_to_xpath('a span'))[0]

        self.assertEquals('contenttype-opengever-task-task',
                          span_tag.get('class'))

    def test_is_prefixed_with_state_icon_per_default(self):
        link = self.add_task_and_get_link()
        self.assertEqual(
            'wf-task-state-tested-and-closed',
            link.xpath(css_to_xpath('span'))[0].get('class'))

    def test_state_prefixe_is_parametrable(self):
        task = self.add_task()
        link = fromstring(task.get_link(with_state_icon=False))
        self.assertEqual(None, link.xpath(css_to_xpath('span'))[0].get('css'))

    def test_link_is_suffixed_with_responsible_info_by_default(self):
        link = self.add_task_and_get_link()
        suffix = link.xpath(css_to_xpath('span'))[2]

        self.assertEquals('(Client1 / Test User (test_user_1_))', suffix.text)
        self.assertEquals('discreet', suffix.get('class'))

    def test_responsible_info_is_parametrable(self):
        task = self.add_task()
        link = fromstring(task.get_link(with_responsible_info=False))

        self.assertEquals(
            'Do it!', link.xpath(css_to_xpath('span'))[-1].text)

    def test_fallback_when_admin_unit_not_exists(self):
        link = self.add_task_and_get_link(admin_unit_id='not-existing')

        self.assertEqual([], link.xpath(css_to_xpath('a')))
        self.assertEqual('span', link.tag)
        self.assertEqual('Do it!', link.text)
        self.assertEqual('icon-task-remote-task', link.get('class'))

    def test_target_blank_for_remote_tasks(self):
        link = self.add_task_and_get_link(admin_unit_id='additional')
        link_tag = link.xpath(css_to_xpath('a'))[0]
        span_tag = link.xpath(css_to_xpath('a span'))[0]

        self.assertEquals('_blank', link_tag.get('target'))
        self.assertEquals('icon-task-remote-task', span_tag.get('class'))

    def test_link_is_xss_safe(self):
        link = self.add_task_and_get_link(
            title="Foo <b onmouseover=alert('Wufff!')>click me!</b>")

        link_tag = link.xpath(css_to_xpath('a span'))[0]
        self.assertEquals('Foo ', link_tag.text)

    def test_handles_non_ascii_characters_correctly(self):
        link = self.add_task_and_get_link(title=u'D\xfc it')
        span_tag = link.xpath(css_to_xpath('a span'))[0]

        self.assertEquals(u'D\xfc it', span_tag.text)
