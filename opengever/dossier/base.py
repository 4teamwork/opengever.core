from Acquisition import aq_inner, aq_parent
from datetime import datetime
from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IConstrainTypeDecider, IDossierContainerTypes
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.interfaces import ICMFDefaultSkin
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import queryMultiAdapter, queryUtility


class DossierContainer(Container):

    def allowedContentTypes(self, *args, **kwargs):
        types = super(DossierContainer, self).allowedContentTypes(*args, **kwargs)
        # calculate depth
        depth = 0
        obj = self
        while IDossierMarker.providedBy(obj):
            depth += 1
            obj = aq_parent(aq_inner(obj))
            if IPloneSiteRoot.providedBy(obj):
                break
        # the adapter decides
        def filter_type(fti):
            # first we try the more specific one ...
            decider = queryMultiAdapter((self.REQUEST, self, fti),
                                    IConstrainTypeDecider,
                                    name=fti.portal_type)
            if not decider:
                # .. then we try the more general one
                decider = queryMultiAdapter((self.REQUEST, self, fti),
                                        IConstrainTypeDecider)
            if decider:
                return decider.addable(depth)
            # if we don't have an adapter, we just allow it
            return True
        # filter
        return filter(filter_type, types)

    def show_subdossier(self):
        registry = queryUtility(IRegistry)
        reg_proxy = registry.forInterface(IDossierContainerTypes)
        depth = 0
        obj = self
        while IDossierMarker.providedBy(obj):
            depth += 1
            obj = aq_parent(aq_inner(obj))
            if IPloneSiteRoot.providedBy(obj):
                break
        if depth > getattr(reg_proxy, 'maximum_dossier_depth', 100):
            return False
        else:
            return True

    def get_subdossiers(self, sort_on='created', sort_order='ascending'):
        dossier_path = '/'.join(self.getPhysicalPath())
        subdossiers = self.portal_catalog(
            path=dict(query=dossier_path,
                      depth=-1),
            sort_on=sort_on,
            sort_order=sort_order,
            object_provides= 'opengever.dossier.behaviors.dossier.IDossierMarker')

        # Remove the object itself from the list of subdossiers
        subdossiers = [s for s in subdossiers if not s.getPath() == dossier_path]
        return subdossiers

    def is_subdossier(self):
        parent = aq_parent(aq_inner(self))
        if IDossierMarker.providedBy(parent):
            return True
        return False

    def is_all_supplied(self):
        """Check if all tasks and all documents are supplied in a subdossier
        provided there are any (active) subdossiers

        """
        subdossiers = self.getFolderContents({
                'object_provides':
                    'opengever.dossier.behaviors.dossier.IDossierMarker'})

        active_dossiers = [d for d in subdossiers
                            if not d.review_state == 'dossier-state-inactive']

        if len(active_dossiers) > 0:
            results = self.getFolderContents({
                    'portal_type': ['opengever.task.task',
                                    'opengever.document.document']})

            if len(results) > 0:
                return False

        return True

    def is_all_closed(self):
        """ Check if all tasks are in a closed state.

        closed:
            - cancelled
            - rejected
            - tested and closed
        """

        tasks_closed = self.portal_catalog(
            portal_type="opengever.task.task",
            path=dict(query='/'.join(self.getPhysicalPath())),
            review_state=('task-state-cancelled',
                          'task-state-rejected',
                          'task-state-tested-and-closed',))

        tasks = self.portal_catalog(
            portal_type="opengever.task.task",
            path=dict(depth=2,
                      query='/'.join(self.getPhysicalPath())))

        if len(tasks_closed) < len(tasks):
            return False
        else:
            return True

    def is_all_checked_in(self):
        """ check if all documents in this path are checked in """

        # all document are checked in
        docs = self.portal_catalog(
            portal_type="opengever.document.document",
            path=dict(depth=2,
                      query='/'.join(self.getPhysicalPath())))

        for doc in docs:
            if doc.checked_out:
                return False

        return True

    def has_valid_enddate(self):
        """Check if the enddate is valid.
        """
        dossier = IDossier(self)
        end_date = self.earliest_possible_end_date()

        # no enddate is valid because it would be overwritten
        # with the earliest_possible_end_date
        if dossier.end is None:
            return True

        if end_date:
            # Dossier end date needs to be older
            # than the earliest possible end_date
            if end_date > dossier.end:
                return False
        return True

    def earliest_possible_end_date(self):

        children = self.getFolderContents(
            {'object_provides':[
                    'opengever.document.behaviors.IBaseDocument',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',]})

        end_dates = []
        for child in children:
            # document or mails
            if child.portal_type == "opengever.document.document":
                if child.document_date:
                    if isinstance(child.document_date, datetime):
                        end_dates.append(child.document_date.date())
                    else:
                        end_dates.append(child.document_date)

            # subdossiers
            else:
                if IDossier(child.getObject()).end:
                    end_date = IDossier(child.getObject()).end
                    if isinstance(end_date, datetime):
                        end_dates.append(end_date.date())
                    else:
                        end_dates.append(end_date)

        if end_dates:
            end_dates.sort()
            return max(end_dates)
        return None

    def computeEndDate(self):
        """Compute a suggested end date for the (sub)dossier, based
        on the dates of its contained objects.

        The final end date is the date of the most recent object that's
        contained (directly or indirectly) in this dossier.
        """
        wft = getToolByName(self, 'portal_workflow')
        end_dates = []

        # Also consider the (sub)dossier's end date
        end_dates.append(IDossier(self).end)

        children = self.getChildNodes()
        for child in children:
            if child.portal_type == "opengever.document.document":
                if child.document_date:
                    end_dates.append(child.document_date)
            elif IDossierMarker.providedBy(child):
                end_dates.append(child.computeEndDate())

        # Remove dates that are 'None'
        end_dates = [d for d in end_dates if d]

        # Make sure all dates are datetime.date instances
        for i, d in enumerate(end_dates):
            if isinstance(d, datetime):
                end_dates[i] = d.date()

        if end_dates:
            end_date = max(end_dates)
        else:
            review_state = wft.getInfoFor(self, 'review_state', None)
            # If a subdossier doesn't have documents, but has a (valid)
            # end date and has been resolved, use its end date
            if (IDossierMarker.providedBy(self)
            and review_state == 'dossier-state-resolved'
            and IDossier(self).end):
                return IDossier(self).end

            # If it has an end date, but isn't necessarily resolved yet,
            # use the end date UNLESS it has subdossiers
            elif (IDossierMarker.providedBy(self)
            and self.get_subdossiers() == []
            and IDossier(self).end):
                return IDossier(self).end

            return None

        # Don't allow end_dates older than start_date
        if end_date < IDossier(self).start:
            end_date = IDossier(self).start
        return end_date

    def check_preconditions(self):
        errors = False
        ptool = getToolByName(self, 'plone_utils')
        # Check if it's a SubDossier
        parent = aq_parent(aq_inner(self))
        if IDossierMarker.providedBy(parent):
            # If so, check for valid end date
            if not self.has_valid_enddate():
                ptool.addPortalMessage(
                    _("no valid end date provided"),
                    type="error")
                return False

            # Everything ok
            return True

        if not self.is_all_supplied():
            errors = True
            ptool.addPortalMessage(
                _("not all documents and tasks are stored in a subdossier"),
                type="error")

        if not self.is_all_checked_in():
            errors = True
            ptool.addPortalMessage(
                _("not all documents are checked in"),
                type="error")

        if not self.is_all_closed():
            errors = True
            ptool.addPortalMessage(
                _("not all task are closed"),
                type="error")

        if errors:
            return False
        return True

    def recursively_resolve(self):
        # Check preconditions for resolving dossier
        preconditions_ok = self.check_preconditions()
        if not preconditions_ok:
            return self.REQUEST.RESPONSE.redirect(self.absolute_url())

        subdossiers_resolved = self.resolve_subdossiers()
        if not subdossiers_resolved:
            return self.REQUEST.RESPONSE.redirect(self.absolute_url())

        dossier_resolved = self.resolve()
        if not dossier_resolved:
            return self.REQUEST.RESPONSE.redirect(self.absolute_url())

        # All ok, show resolving mask
        return self.REQUEST.RESPONSE.redirect(self.absolute_url() + \
                                              '/transition-archive')

    def resolve_subdossiers(self):
        """Resolves all subdossiers of this dossier, if possible.
        Otherwise, throw an error message and return to the context
        """
        ptool = getToolByName(self, 'plone_utils')
        wft = getToolByName(self, 'portal_workflow')
        subdossiers = self.get_subdossiers()

        for subdossier in subdossiers:
            subdossier = subdossier.getObject()
            status =  wft.getStatusOf("opengever_dossier_workflow", subdossier)
            state = status["review_state"]

            if not state in ('dossier-state-resolved', 'dossier-state-inactive'):
                if subdossier.computeEndDate():
                    # Resolve subdossier after setting end date and filing_no
                    if not IDossier(subdossier).end:
                        IDossier(subdossier).end = subdossier.computeEndDate()

                    else:
                        # Validate the existing end date
                        if IDossier(subdossier).end < subdossier.computeEndDate():
                            ptool.addPortalMessage(_("The subdossier '${title}' has an invalid end date." ,
                                                      mapping=dict(title=subdossier.Title())
                                                      ), type="error")
                            return False


                    wft.doActionFor(subdossier, 'dossier-transition-resolve')
                else:
                    # The subdossier's end date can't be determined automatically
                    ptool.addPortalMessage(_("The subdossier '${title}' needs to be resolved manually.",
                                              mapping=dict(title=subdossier.Title())
                                              ), type="error")
                    return False
        return True

    def resolve(self):
        """Try to resolve this dossier.

        For that to happen, first all subdossiers need to have filing_no
        and end_date set, and then be resolved. If resolving any of the
        subdossier fails, we'll throw and error and return.
        """

        ptool = getToolByName(self, 'plone_utils')
        wft = getToolByName(self, 'portal_workflow')

        parent = aq_parent(aq_inner(self))

        if IDossierMarker.providedBy(parent):
            # It's a subdossier
            end_date = self.computeEndDate()
            if end_date:
                IDossier(self).end = end_date
                wft.doActionFor(self, 'dossier-transition-resolve')
                return True
            else:
                ptool.addPortalMessage(_("The subdossier '${title}' needs to be resolved manually.",
                                          mapping=dict(title=self.Title())
                                          ), type="error")
                return False
        else:
            # It's a main dossier
            return True


class DefaultConstrainTypeDecider(grok.MultiAdapter):
    grok.provides(IConstrainTypeDecider)
    grok.adapts(ICMFDefaultSkin, IDossierMarker, IDexterityFTI)
    grok.name('')

    CONSTRAIN_CONFIGURATION = {
        'opengever.dossier.businesscasedossier' : {
            'opengever.dossier.businesscasedossier' : 2,
            'opengever.dossier.projectdossier' : 1,
            },
        'opengever.dossier.projectdossier' : {
            'opengever.dossier.projectdossier' : 1,
            'opengever.dossier.businesscasedossier' : 1,
            },
        }


    def __init__(self, request, context, fti):
        self.context = context
        self.request = request
        self.fti = fti

    def addable(self, depth):
        container_type = self.context.portal_type
        factory_type = self.fti.id
        mapping = self.constrain_type_mapping
        for const_ctype, const_depth, const_ftype in mapping:
            if const_ctype==container_type and const_ftype==factory_type:
                return depth<const_depth or const_depth==0
        return True

    @property
    def constrain_type_mapping(self):
        conf = self.__class__.CONSTRAIN_CONFIGURATION
        for container_type, type_constr in conf.items():
            for factory_type, max_depth in type_constr.items():
                yield container_type, max_depth, factory_type

