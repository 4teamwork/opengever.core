from opengever.base.handlebars import prepare_handlebars_template
from path import Path
from Products.Five.browser import BrowserView


TEMPLATES_DIR = Path(__file__).joinpath('..', 'templates').abspath()


class ConfigView(BrowserView):
    """Provides a read only view of the current site configurables.

    Implemented client-sided over JS and the API endpoint.
    """

    def render_form_template(self):
        return prepare_handlebars_template(TEMPLATES_DIR.joinpath('config.html'))
