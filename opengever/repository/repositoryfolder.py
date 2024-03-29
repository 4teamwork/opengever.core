from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.interfaces import IReferenceNumber
from opengever.dossier.utils import check_subdossier_depth_allowed
from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder
from plone.app.content.interfaces import INameFromTitle
from plone.dexterity import content
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements


REPOSITORY_FOLDER_STATE_INACTIVE = 'repositoryfolder-state-inactive'


class IRepositoryFolderSchema(model.Schema):
    """ A Repository Folder
    """

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'description',
            u'valid_from',
            u'valid_until',
            u'location',
            u'referenced_activity',
            u'former_reference',
            u'allow_add_businesscase_dossier',
            u'respect_max_subdossier_depth_restriction',
        ],
    )

    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description=_(
            u'help_description',
            default=u'A short summary of the content.'),
        required=False,
        default=u'',
        missing_value=u'',
    )

    valid_from = schema.Date(
        title=_(u'label_valid_from', default=u'Valid from'),
        required=False,
    )

    valid_until = schema.Date(
        title=_(u'label_valid_until', default=u'Valid until'),
        required=False,
    )

    location = schema.TextLine(
        title=_(u'label_location', default=u'Location'),
        required=False,
    )

    referenced_activity = schema.TextLine(
        title=_(
            u'label_referenced_activity',
            default=u'Referenced activity'),
        required=False,
    )

    former_reference = schema.TextLine(
        title=_(u'label_former_reference', default=u'Former reference'),
        required=False,
    )

    allow_add_businesscase_dossier = schema.Bool(
        title=_(u'allow_add_businesscase_dossier',
                default=u'Allow add businesscase dossier'),
        description=_(u'description_allow_add_businesscase_dossier',
                      default=u'Choose if the user is allowed to add '
                              u'businesscase dossiers or only dossiers from a '
                              u' dossiertemplate.'),
        required=False,
        missing_value=True,
        default=True,
    )

    respect_max_subdossier_depth_restriction = schema.Bool(
        title=_(u'label_respect_max_subdossier_depth_restriction',
                default=u'Limit maximum dossier depth in this repository folder'),
        description=_(u'description_max_subdossier_depth_restriction',
                      default=u'Select if this repostory tree should respect '
                              u'the max subdossier depth restriction.'),
        required=False,
        missing_value=True,
        default=True,
    )


class RepositoryFolder(content.Container):

    implements(IRepositoryFolder)

    def Title(self, language=None, prefix_with_reference_number=True):
        title = ITranslatedTitle(self).translated_title(language)
        if prefix_with_reference_number:
            title = self._prefix_with_reference_number(title)
        if isinstance(title, unicode):
            return title.encode('utf-8')
        return title or ''

    def get_retention_period(self):
        return ILifeCycle(self).retention_period

    def get_retention_period_annotation(self):
        return ILifeCycle(self).retention_period_annotation

    def get_archival_value_annotation(self):
        return ILifeCycle(self).archival_value_annotation

    def get_custody_period(self):
        return ILifeCycle(self).custody_period

    def get_repository_number(self):
        return IReferenceNumber(self).get_repository_number()

    def get_repository_number_separator(self):
        return IReferenceNumber(self).get_active_formatter().repository_title_seperator

    def get_prefixed_title_de(self):
        title = self.title_de
        if title:
            return self._prefix_with_reference_number(title)

    def get_prefixed_title_fr(self):
        title = self.title_fr
        if title:
            return self._prefix_with_reference_number(title)

    def get_prefixed_title_en(self):
        title = self.title_en
        if title:
            return self._prefix_with_reference_number(title)

    def get_archival_value(self):
        return ILifeCycle(self).archival_value

    def _prefix_with_reference_number(self, title):
        return u'{number}{sep} {title}'.format(
            number=self.get_repository_number(),
            sep=self.get_repository_number_separator(),
            title=title)

    def is_leaf_node(self):
        """ Checks if the current repository folder is a leaf-node.
        """
        for obj in self.objectValues():
            # A repository folder cannot contain other repository folders and
            # items of other content types at the same time.
            if obj.portal_type == self.portal_type:
                return False
            else:
                return True
        return True

    def is_dossier_structure_addable(self, depth=1):
        if not self.respect_max_subdossier_depth_restriction:
            return True
        return check_subdossier_depth_allowed(depth - 1)


@implementer(INameFromTitle)
@adapter(IRepositoryFolder)
class NameFromTitle(object):
    """ An INameFromTitle adapter for namechooser gets the name from the
    translated_title.
    """

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return ITranslatedTitle(self.context).translated_title()
