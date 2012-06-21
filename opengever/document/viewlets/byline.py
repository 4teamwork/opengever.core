from Products.CMFCore.utils import getToolByName
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.document.document import IDocumentSchema
from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize
from zope.component import getUtility, getAdapter
from opengever.base.browser.helper import get_css_class


class DocumentByline(content.DocumentBylineViewlet):

    update = content.DocumentBylineViewlet.update

    def get_css_class(self):
        return get_css_class(self.context)

    def start(self):
        document = IDocumentSchema(self.context)
        return document.start

    def responsible(self):
        mt = getToolByName(self.context, 'portal_membership')
        document = IDocumentSchema(self.context)
        return mt.getMemberById(document.responsible)

    def end(self):
        document = IDocumentSchema(self.context)
        return document.end

    @memoize
    def workflow_state(self):
        state = self.context_state.workflow_state()
        workflows = self.context.portal_workflow.getWorkflowsFor(
            self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state

    @memoize
    def sequence_number(self):
        seqNumb = getUtility(ISequenceNumber)
        return seqNumb.get_number(self.context)

    @memoize
    def reference_number(self):
        refNumb = getAdapter(self.context, IReferenceNumber)
        return refNumb.get_number()

    def get_filing_no(self):
        document = IDocumentSchema(self.context)
        return getattr(document, 'filing_no', None)
