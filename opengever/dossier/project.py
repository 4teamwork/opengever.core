
from zope import schema

from plone.directives import form
from opengever.base.browser.helper import get_css_class
from five import grok
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.memoize.instance import memoize
from plone.app.layout.viewlets import content
from opengever.dossier.behaviors.dossier import IDossier



class IProjectDossier(form.Schema):
    """ A project dossier
    """

    # just an example field for a project dossier
    project_manager = schema.TextLine(
            title = u'Project Manager',
            required = False
    )

class Byline(grok.Viewlet, content.DocumentBylineViewlet):
    grok.viewletmanager(IBelowContentTitle)
    grok.context(IProjectDossier)
    grok.name("plone.belowcontenttitle.documentbyline")

    update = content.DocumentBylineViewlet.update

    def get_css_class(self):
        return get_css_class(self.context)


    def start(self):
        dossier = IDossier(self.context)
        return dossier.start

    def end(self):
        dossier = IDossier(self.context)
        return dossier.end

    @memoize
    def workflow_state(self):
        #context = aq_inner(self.context)
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state