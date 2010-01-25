from five import grok
from zope.component import getUtility, getAdapter

from plone.app.layout.viewlets import content
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.directives import form
from plone.directives import dexterity
from plone.memoize.instance import memoize

from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossier, IDossierMarker
from opengever.mail.behaviors import IMailInAddressMarker,IMailInAddress
from opengever.octopus.tentacle.interfaces import IContactInformation

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
#
#     def updateWidgets(self):
#         super(Edit, self).updateWidgets()
#         #self.widgets['title'].mode = 'hidden'
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

    def responsible(self):
        info = getUtility(IContactInformation)
        dossier = IDossier(self.context)
        return info.render_link(dossier.responsible)

    def end(self):
        dossier = IDossier(self.context)
        return dossier.end

    @memoize
    def workflow_state(self):
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
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
        dossier = IDossierMarker(self.context)
        return getattr(dossier, 'filing_no', None)

    # TODO: should be more generic ;-)
    #       use sequence_number instead of intid
    def email(self):
        if IMailInAddressMarker.providedBy(self.context):
            return IMailInAddress(self.context).get_email_address()
