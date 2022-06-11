from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.interface import classProvides
from zope.interface import implements
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class WorkflowUpdaterSection(object):
    """Section that sets the workflow state of objects during OGGBundle import.

    We do this instead of executing WF transitions so we can reliably create
    objects in a particular WF state, without being blocked by transition
    guards, business rules or cause side effects from event handlers.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.wftool = getToolByName(self.context, 'portal_workflow')

    def __iter__(self):
        for item in self.previous:
            pathkey = '_path'
            statekey = 'review_state'

            if not (pathkey and statekey):  # not enough info
                yield item
                continue

            if statekey not in item:  # no WF state given
                yield item
                continue

            path, state = item[pathkey], item[statekey]

            obj = traverse(self.context, path, None)
            if obj is None:
                log.warning(
                    "Cannot set workflow state for %s. "
                    "Object doesn't exist" % path)
                yield item
                continue

            try:
                wf_ids = self.wftool.getChainFor(obj)
                if wf_ids:
                    wf_id = wf_ids[0]
                    comment = 'Set workflow state upon import.'
                    self.wftool.setStatusOf(
                        wf_id, obj,
                        {'review_state': state,
                         'action': state,
                         'actor': 'GEVER migration',
                         'time': DateTime(),
                         'comments': comment})

                    wfs = {wf_id: self.wftool.getWorkflowById(wf_id)}
                    self.wftool._recursiveUpdateRoleMappings(obj, wfs)

                    # Since the `View` permissions isn't affected, there's
                    # no need for obj.reindexObjectSecurity() here

            except WorkflowException as exc:
                log.warning(
                    "Cannot set workflow state for %s. "
                    "An exception occured: %r" % (path, exc))
                pass

            yield item
