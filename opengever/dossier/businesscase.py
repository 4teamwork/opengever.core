from plone.directives import form
from plone.directives import dexterity
from five import grok
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.memoize.instance import memoize
from Acquisition import aq_inner
from plone.app.layout.viewlets import content
from opengever.dossier.behaviors.dossier import IDossier

class IBusinessCaseDossier(form.Schema):
    """ A business case dossier
    """


# class Edit(dexterity.EditForm):
#     """A standard edit form.
#     """
#     grok.context(IBusinessCaseDossier)
#     
#     def update(self):
#         super(Edit, self).update()
#         #import pdb; pdb.set_trace()
# 
#     def updateWidgets(self):
#         super(Edit, self).updateWidgets()
#         #self.widgets['title'].mode = 'hidden'
#         #import pdb; pdb.set_trace()
#         #self.widgets['IDossier.comments'].rows = 10
#         #self.widgets['IDossier.comments'].requires = True


class View(dexterity.DisplayForm):
    grok.context(IBusinessCaseDossier)
    grok.require('zope2.View')
    
    
class Byline(grok.Viewlet, content.DocumentBylineViewlet):
    grok.viewletmanager(IBelowContentTitle)
    grok.context(IBusinessCaseDossier)
    grok.name("plone.belowcontenttitle.documentbyline")

    update = content.DocumentBylineViewlet.update

    def start(self):
        dossier = IDossier(self.context)
        return dossier.start

    def end(self):
        dossier = IDossier(self.context)
        return dossier.end
    
    @memoize
    def workflow_state(self):
        context = aq_inner(self.context)
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state
