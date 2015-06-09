from opengever.base import _
from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
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

    def modified(self):
        return self.to_localized_time(self.context.ModificationDate(),
                                      long_format=1)

    def created(self):
        return self.to_localized_time(self.context.CreationDate(),
                                      long_format=1)

    @memoize
    def workflow_state(self):
        return self.plone_messagefactory(self.get_current_state())

    def to_localized_time(self, time, long_format=0):
        adapter = getMultiAdapter((self.context, self.request), name="plone")
        return adapter.toLocalizedTime(str(time), long_format)

    def get_items(self):
        return [
            {'class': 'document_created',
             'label': _('label_created', default='Created'),
             'content': self.created(),
             'replace': False},

            {'class': 'last_modified',
             'label': _('label_last_modified', default='Last modified'),
             'content': self.modified(),
             'replace': False},
        ]


class PloneSiteByline(BylineBase):

    def get_css_class(self):
        """No sensible icon exists for the PloneSite respectively
        personal overview, so we return None."""

        return None
