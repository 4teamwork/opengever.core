from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.utils import hide_fields_from_behavior
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.base.interfaces import IReferenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.interfaces import IRepositoryFolderRecords
from plone import api
from plone.app.content.interfaces import INameFromTitle
from plone.dexterity import content
from plone.directives import form
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import queryUtility
from zope.interface import implements


class IRepositoryFolderSchema(form.Schema):
    """ A Repository Folder
    """

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'description',
            u'valid_from',
            u'valid_until',
            u'location',
            u'referenced_activity',
            u'former_reference',
            ],
        )

    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description=_(
            u'help_description',
            default=u'A short summary of the content.'),
        required=False,
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

    form.widget(addable_dossier_types=CheckBoxFieldWidget)
    addable_dossier_types = schema.List(
        title=_(u'label_addable_dossier_types',
                default=u'Addable dossier types'),
        description=_(u'help_addable_dossier_types',
                      default=u'Select all additional dossier types which '
                      'should be addable in this repository folder.'),
        value_type=schema.Choice(
            vocabulary=u'opengever.repository.RestrictedAddableDossiersVocabulary'),
        required=False)

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


class RepositoryFolder(content.Container):

    implements(IRepositoryFolder)

    def Title(self, language=None, prefix_with_reference_number=True):
        title = ITranslatedTitle(self).translated_title(language)
        if prefix_with_reference_number:
            title = self._prefix_with_reference_number(title)
        if isinstance(title, unicode):
            return title.encode('utf-8')
        return title or ''

    def get_prefixed_title_de(self):
        title = self.title_de
        if title:
            return self._prefix_with_reference_number(title)

    def get_prefixed_title_fr(self):
        title = self.title_fr
        if title:
            return self._prefix_with_reference_number(title)

    def get_archival_value(self):
        return ILifeCycle(self).archival_value

    def _prefix_with_reference_number(self, title):
        reference_adapter = IReferenceNumber(self)
        return u'{number}{sep} {title}'.format(
            number=reference_adapter.get_repository_number(),
            sep=reference_adapter.get_active_formatter().repository_title_seperator,
            title=title)

    def is_leaf_node(self):
        """ Checks if the current repository folder is a leaf-node.
        """
        for id, obj in self.contentItems():
            if obj.portal_type == self.portal_type:
                return False
        return True

    def allowedContentTypes(self, *args, **kwargs):
        """
        We have to follow some rules:
        1. If this RepositoryFolder contains another RF, we should not be
        able to add other types than RFs.
        2. If we are reaching the maximum depth of repository folders
        (Configured in plone.registry), we should not be able to add
        any more RFs, but then we should be able to add the other configured
        types in any case. If the maximum_repository_depth is set to 0,
        we do not have a depth limit.
        """
        # get the default types
        types = super(
            RepositoryFolder, self).allowedContentTypes(*args, **kwargs)
        # get fti of myself
        fti = self.portal_types.get(self.portal_type)
        # get maximum depth of repository folders
        registry = queryUtility(IRegistry)
        proxy = registry.forInterface(IRepositoryFolderRecords)
        # 0 -> no restriction
        maximum_depth = getattr(proxy, 'maximum_repository_depth', 0)
        current_depth = 0
        # if we have a maximum depth, we need to know the current depth
        if maximum_depth > 0:
            obj = self
            while IRepositoryFolder.providedBy(obj):
                current_depth += 1
                obj = aq_parent(aq_inner(obj))
                if IPloneSiteRoot.providedBy(obj):
                    break
            if maximum_depth <= current_depth:
                # depth exceeded
                # RepositoryFolder not allowed, but any other type
                types = filter(lambda a: a != fti, types)

        # filter content types, if required
        if not self.is_leaf_node():
            # only allow same types
            types = filter(lambda a: a == fti, types)

        # finally: remove not enabled resticted content types
        marker_behavior = 'opengever.dossier.behaviors.restricteddossier.' + \
            'IRestrictedDossier'

        allowed = self.addable_dossier_types \
            and self.addable_dossier_types or []

        def _filterer(fti):
            if fti.id in allowed:
                # fti is enabled in repository folder
                return True

            elif getattr(fti, 'behaviors', None) \
                    and marker_behavior in fti.behaviors:
                # fti has marker interface and is not enabled
                return False

            else:
                # normal type - we don't care
                return True

        types = filter(_filterer, types)

        return types


class AddForm(TranslatedTitleAddForm):
    grok.name('opengever.repository.repositoryfolder')

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
        hide_fields_from_behavior(self,
                                  ['IClassification.public_trial',
                                   'IClassification.public_trial_statement'])


class EditForm(TranslatedTitleEditForm):
    grok.context(IRepositoryFolder)

    def updateFields(self):
        super(EditForm, self).updateFields()
        hide_fields_from_behavior(self,
                                  ['IClassification.public_trial',
                                   'IClassification.public_trial_statement'])


class NameFromTitle(grok.Adapter):
    """ An INameFromTitle adapter for namechooser gets the name from the
    translated_title.
    """
    grok.implements(INameFromTitle)
    grok.context(IRepositoryFolder)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return ITranslatedTitle(self.context).translated_title()
