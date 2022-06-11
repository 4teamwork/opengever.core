from opengever.base import handlebars
from path import Path
from unittest import TestCase
from zope.i18nmessageid import MessageFactory


TEMPLATES_DIR = Path(__file__).joinpath('..', 'templates').abspath()
SIMPLE_TEMPLATE = TEMPLATES_DIR.joinpath('simple_template.html')
_ = MessageFactory('test')


class TestHandlebars(TestCase):

    def test_prepare_with_translations(self):
        template = handlebars.prepare_handlebars_template(
            SIMPLE_TEMPLATE,
            translations=(_('foo', 'Foo 2'),
                          _('bar', 'Bar 2')))
        self.assertIn('<div class="foo">Foo 2</div>', template)
        self.assertIn('<div class="bar">Bar 2</div>', template)

    def test_prepare_with_params(self):
        template = handlebars.prepare_handlebars_template(
            SIMPLE_TEMPLATE,
            foo='Foo 1',
            bar='Bar 1')
        self.assertIn('<div class="foo">Foo 1</div>', template)
        self.assertIn('<div class="bar">Bar 1</div>', template)

    def test_prepare_with_translations_and_params(self):
        template = handlebars.prepare_handlebars_template(
            SIMPLE_TEMPLATE,
            translations=(_('foo', 'Foo 2'), ),
            bar='Bar 1')
        self.assertIn('<div class="foo">Foo 2</div>', template)
        self.assertIn('<div class="bar">Bar 1</div>', template)

    def test_get_template(self):
        template = handlebars.get_handlebars_template(SIMPLE_TEMPLATE)
        self.assertIn('<div class="foo">%(foo)s</div>', template)
        self.assertIn('<div class="bar">%(bar)s</div>', template)
