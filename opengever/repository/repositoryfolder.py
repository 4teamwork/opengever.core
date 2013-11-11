from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from opengever.repository import _
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefixMarker
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.interfaces import IRepositoryFolderRecords
from plone.app.content.interfaces import INameFromTitle
from plone.dexterity import content
from plone.directives import form
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.interface import implements
import zope.component


class IRepositoryFolderSchema(form.Schema):
    """ A Repository Folder
    """

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'effective_title',
            u'description',
            u'valid_from',
            u'valid_until',
            u'location',
            u'referenced_activity',
            u'former_reference',
            ],
        )

    #form.omitted('title')
    form.order_before(effective_title='*')
    effective_title = schema.TextLine(
        title=_(u'Title'),
        required=True,
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
        description=_(u'help_valid_from', default=u''),
        required=False,
        )

    valid_until = schema.Date(
        title=_(u'label_valid_until', default=u'Valid until'),
        description=_(u'help_valid_until', default=u''),
        required=False,
        )

    location = schema.TextLine(
        title=_(u'label_location', default=u'Location'),
        description=_(u'help_location', default=u''),
        required=False,
        )

    referenced_activity = schema.TextLine(
        title=_(
            u'label_referenced_activity',
            default=u'Referenced activity'),
        description=_(u'help_referenced_activity', default=u''),
        required=False,
        )

    former_reference = schema.TextLine(
        title=_(u'label_former_reference', default=u'Former reference'),
        description=_(u'help_former_reference', default=u''),
        required=False,
        )

    addable_dossier_types = schema.List(
        title=_(u'label_addable_dossier_types',
                default=u'Addable dossier types'),
        description=_(u'help_addable_dossier_types',
                      default=u'Select all additional dossier types which '
                      'should be addable in this repository folder.'),
        value_type=schema.Choice(vocabulary=u'opengever.repository.'
                                 u'RestrictedAddableDossiersVocabulary'),
        required=False)


class RepositoryFolder(content.Container):

    implements(IRepositoryFolder)

    def Title(self):
        title = u' %s' % self.effective_title
        obj = self
        while IRepositoryFolder.providedBy(obj):
            if IReferenceNumberPrefixMarker.providedBy(obj):
                rfnr = IReferenceNumberPrefix(obj).reference_number_prefix
                title = unicode(rfnr) + '.' + title
            obj = aq_parent(aq_inner(obj))

        return title.encode('utf-8')

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
        registry = zope.component.queryUtility(IRegistry)
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
        # check if self contains any similar objects
        contains_similar_objects = False
        for id, obj in self.contentItems():
            if obj.portal_type == self.portal_type:
                contains_similar_objects = True
                break

        # filter content types, if required
        if contains_similar_objects:
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


class NameFromTitle(grok.Adapter):
    """ An INameFromTitle adapter for namechooser
    gets the name from effective_title
    """
    grok.implements(INameFromTitle)
    grok.context(IRepositoryFolder)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.effective_title
