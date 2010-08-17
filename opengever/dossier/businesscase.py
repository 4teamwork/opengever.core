from five import grok

from plone.directives import form
from plone.directives import dexterity


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
