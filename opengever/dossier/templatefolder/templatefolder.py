from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.dossier.dossiertemplate import is_dossier_template_feature_enabled
from opengever.dossier.templatefolder import ITemplateFolder
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting import is_word_meeting_implementation_enabled
from plone.dexterity.content import Container


class TemplateFolderAddForm(TranslatedTitleAddForm):
    grok.name('opengever.dossier.templatefolder')


class TemplateFolderEditForm(TranslatedTitleEditForm):
    grok.context(ITemplateFolder)


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
            if factory_type in [u'opengever.meeting.sablontemplate']:
                return is_meeting_feature_enabled()

            if factory_type in [u'opengever.meeting.proposaltemplate']:
                return is_word_meeting_implementation_enabled()

            if factory_type in [u'opengever.dossier.dossiertemplate']:
                return is_dossier_template_feature_enabled()

            return True

        return filter(filter_type, types)
