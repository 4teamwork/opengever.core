from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.dossier.dossiertemplate import is_dossier_template_feature_enabled
from opengever.dossier.templatefolder import ITemplateFolder
from opengever.meeting import is_meeting_feature_enabled
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class AddForm(TranslatedTitleAddForm):
    """
    """


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class AddView(DefaultAddView):
    form = AddForm


class EditForm(TranslatedTitleEditForm):
    """
    """


class TemplateFolder(Container, TranslatedTitleMixin):
    """Base class for template folder."""

    Title = TranslatedTitleMixin.Title

    def is_subtemplatefolder(self):
        parent = aq_parent(aq_inner(self))
        return bool(ITemplateFolder.providedBy(parent))

    def allowedContentTypes(self, *args, **kwargs):
        types = super(TemplateFolder, self).allowedContentTypes(*args, **kwargs)

        def filter_type(fti):
            factory_type = fti.id
            if factory_type in [u'opengever.meeting.sablontemplate',
                                u'opengever.meeting.proposaltemplate',
                                u'opengever.meeting.meetingtemplate']:
                return is_meeting_feature_enabled()

            if factory_type in [u'opengever.dossier.dossiertemplate']:
                return is_dossier_template_feature_enabled()

            return True

        return filter(filter_type, types)
