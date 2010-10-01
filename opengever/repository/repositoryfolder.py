from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok

from zope import schema
import zope.component
from zope.interface import implements
from plone.app.content.interfaces import INameFromTitle
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.dexterity import content
from plone.directives import form
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry

from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.behaviors.referenceprefix import \
    IReferenceNumberPrefix, IReferenceNumberPrefixMarker
from opengever.repository.interfaces import IRepositoryFolderRecords


class IRepositoryFolderSchema(form.Schema):
    """ A Repository Folder
    """

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
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
    form.order_before(effective_title = '*')
    effective_title = schema.TextLine(
        title = _(u'Title'),
        required = True,
        )

    description = schema.Text(
        title = _(u'label_description', default=u'Description'),
        description = _(
            u'help_description',
            default=u'A short summary of the content.'),
        required = False,
        )

    form.widget(valid_from='ftw.datepicker.widget.DatePickerFieldWidget')
    valid_from = schema.Date(
        title = _(u'label_valid_from', default=u'Valid from'),
        description = _(u'help_valid_from', default=u''),
        required = False,
        )

    form.widget(valid_until='ftw.datepicker.widget.DatePickerFieldWidget')
    valid_until = schema.Date(
        title = _(u'label_valid_until', default=u'Valid until'),
        description = _(u'help_valid_until', default=u''),
        required = False,
        )

    location = schema.TextLine(
         title = _(u'label_location', default=u'Location'),
         description = _(u'help_location', default=u''),
         required = False,
         )

    referenced_activity = schema.TextLine(
         title = _(
            u'label_referenced_activity',
            default=u'Referenced activity'),
         description = _(u'help_referenced_activity', default=u''),
         required = False,
         )

    former_reference = schema.TextLine(
         title = _(u'label_former_reference', default=u'Former reference'),
         description = _(u'help_former_reference', default=u''),
         required = False,
         )


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
        return title

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
        if maximum_depth>0:
            obj = self
            while IRepositoryFolder.providedBy(obj):
                current_depth += 1
                obj = aq_parent(aq_inner(obj))
                if IPloneSiteRoot.providedBy(obj):
                    break
            if maximum_depth<=current_depth:
                # depth exceeded
                # RepositoryFolder not allowed, but any other type
                return filter(lambda a: a!= fti, types)
        # check if self contains any similar objects
        contains_similar_objects = False
        for id, obj in self.contentItems():
            if obj.portal_type==self.portal_type:
                contains_similar_objects = True
                break
        # filter content types, if required
        if contains_similar_objects:
            # only allow same types
            types = filter(lambda a: a== fti, types)
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


class Byline(grok.Viewlet):
    grok.viewletmanager(IBelowContentTitle)
    grok.context(IRepositoryFolder)
    grok.name("plone.belowcontenttitle.documentbyline")

    #update = content.DocumentBylineViewlet.update
    @memoize
    def workflow_state(self):
        context_state = self.context.restrictedTraverse("@@plone_context_state")
        return context_state.workflow_state()
