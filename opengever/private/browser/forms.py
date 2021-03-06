from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.dossier.browser.forms import DossierAddView
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class PrivateRootAddView(DefaultAddView):
    form = TranslatedTitleAddForm


class PrivateDossierAddView(DossierAddView):
    """Add view for opengever.private.dossier
    """
