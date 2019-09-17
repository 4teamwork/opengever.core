from opengever.base import _
from opengever.base.handlebars import get_handlebars_template
from opengever.readonly.utils import gever_is_readonly
from pkg_resources import resource_filename
from plone import api
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json


READONLY_MARKUP = """
<div style="display: block; border:1px solid black; padding: 1em; background-color: rgb(234, 153, 153) !important; text-align: center">

    <strong>GEVER is currently in readonly mode</strong>

</div>
"""


class GlobalMessageViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('globalmessage.pt')

    def available(self):
        return True

    def markup(self):
        if gever_is_readonly():
            return READONLY_MARKUP
        return ''
