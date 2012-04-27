from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize
from zope.component import getUtility, getAdapter
from opengever.base.browser.helper import get_css_class


class OGMailByline(content.DocumentBylineViewlet):

    update = content.DocumentBylineViewlet.update

    def get_css_class(self):
        return get_css_class(self.context)

    @memoize
    def sequence_number(self):
        seqNumb = getUtility(ISequenceNumber)
        return seqNumb.get_number(self.context)

    @memoize
    def reference_number(self):
        refNumb = getAdapter(self.context, IReferenceNumber)
        return refNumb.get_number()
