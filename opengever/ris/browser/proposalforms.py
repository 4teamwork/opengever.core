from opengever.ris import is_ris_feature_enabled
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from zExceptions import Unauthorized
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ProposalEditForm(DefaultEditForm):

    def render(self):
        if not is_ris_feature_enabled():
            raise Unauthorized

        return super(ProposalEditForm, self).render()


class ProposalAddForm(DefaultAddForm):

    def render(self):
        if not is_ris_feature_enabled():
            raise Unauthorized
        return super(ProposalAddForm, self).render()


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class ProposalAddView(DefaultAddView):
    form = ProposalAddForm
