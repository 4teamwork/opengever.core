from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtility, getAdapter
from zope.i18nmessageid import MessageFactory


class BylineBase(content.DocumentBylineViewlet):
    """ Byline base class. Provides methods and template to generate byline."""

    index = ViewPageTemplateFile("byline.pt")

    plone_messagefactory = MessageFactory("plone")

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

    def get_current_state(self):
        state = self.context_state.workflow_state()
        workflows = self.context.portal_workflow.getWorkflowsFor(
            self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state

    @memoize
    def workflow_state(self):
        return self.plone_messagefactory(self.get_current_state())

    def to_localized_time(self, time, long_format=0):
        adapter = getMultiAdapter((self.context, self.request), name="plone")
        return adapter.toLocalizedTime(str(time), long_format)
