from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.base.formutils import hide_field_by_name
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository import _
from plone import api
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class AddForm(TranslatedTitleAddForm):

    def render(self):
        if self.contains_dossiers():
            msg = _('msg_leafnode_warning',
                    default=u'You are adding a repositoryfolder to a leafnode '
                    'which already contains dossiers. This is only '
                    'temporarily allowed and all dossiers must be moved into '
                    'a new leafnode afterwards.')

            api.portal.show_message(
                msg, request=self.request, type='warning')

        return super(AddForm, self).render()

    def contains_dossiers(self):
        dossiers = api.content.find(context=self.context,
                                    depth=1,
                                    object_provides=IDossierMarker)
        return bool(dossiers)

    def updateFields(self):
        super(AddForm, self).updateFields()
        hide_field_by_name(self, 'IClassification.public_trial')
        hide_field_by_name(self, 'IClassification.public_trial_statement')


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class AddView(DefaultAddView):
    form = AddForm


class EditForm(TranslatedTitleEditForm):

    def updateFields(self):
        super(EditForm, self).updateFields()
        hide_field_by_name(self, 'IClassification.public_trial')
        hide_field_by_name(self, 'IClassification.public_trial_statement')
