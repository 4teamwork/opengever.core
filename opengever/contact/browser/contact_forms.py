from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ContactAddForm(DefaultAddForm):

    def render(self):
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        if fti not in self.context.allowedContentTypes():
            raise Unauthorized

        return super(ContactAddForm, self).render()


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class ContactAddView(DefaultAddView):
    form = ContactAddForm
