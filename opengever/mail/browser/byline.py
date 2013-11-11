from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.base.viewlets.byline import BylineBase
from opengever.mail import _
from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize
from zope.component import getUtility, getAdapter


class OGMailByline(BylineBase):

    def get_items(self):
        return [
            {'class': 'created',
             'label': _('byline_created', default='Created'),
             'content': self.created(),
             'replace': False},

            {'class': 'sequenceNumber',
             'label': _('label_sequence_number', default='Sequence Number'),
             'content': self.sequence_number(),
             'replace': False},

            {'class': 'reference_number',
             'label': _('label_reference_number', default='Reference Number'),
             'content': self.reference_number(),
             'replace': False},
        ]
