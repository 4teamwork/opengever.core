from five import grok
from logging import getLogger

from Missing import Value as MissingValue
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

from opengever.base import _
from opengever.base.interfaces import ISequenceNumber
from opengever.base.sequence import SEQUENCE_NUMBER_ANNOTATION_KEY
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.sequence import DossierSequenceNumberGenerator
from opengever.repository.repositoryroot import IRepositoryRoot


logger = getLogger('opengever.base')

class IAdjustSequenceNumbersSchema(form.Schema):

    new_counter_value = schema.Int(
            title=_(u"Enter the new value for the dossier sequence number counter"),
            min=0,
            required=True
        )

    target_repos = RelationList(
        title=_(u'label_target_repos', default=u'Target Repositories'),
        default=[],
        value_type=RelationChoice(
            title=u"Targets",
            source=ObjPathSourceBinder(
                object_provides=IRepositoryRoot.__identifier__,
                navigation_tree_query={
                    'object_provides':
                        ['opengever.repository.repositoryroot.IRepositoryRoot',]
                    }),
            ),
        required=True,
        )

class AdjustSequenceNumbersForm(form.SchemaForm):
    grok.name('adjust-sequence-numbers')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = IAdjustSequenceNumbersSchema
    ignoreContext = True

    label = _(u"Adjust Dossier Sequence Number Counter")
    description = _(u"Modify the internal counter used for generating dossier sequence numbers")

    def update(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)

        # call the base class version - this is very important!
        super(AdjustSequenceNumbersForm, self).update()


    def get_current_counter_value(self):
        # Retrieve the current counter value and
        # store it in the form
        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        if SEQUENCE_NUMBER_ANNOTATION_KEY not in ann.keys():
            # Sequence number generator hasn't been initialized yet
            IStatusMessage(self.request).addStatusMessage(
                    _(u"Sequence number generator hasn't been initialized yet"), 
                    "error")
            context_url = self.context.absolute_url()
            self.request.response.redirect(context_url)
            return

        key = DossierSequenceNumberGenerator.key
        sn_counters = ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY)
        increaser = sn_counters[key]
        current_value = increaser()
        return current_value


    @button.buttonAndHandler(_(u'Adjust'))
    def handleApply(self, action):
        """
        Sets the internal sequence number counter for Dossiers
        to the value supplied in the form, and then migrates all
        the affected dossiers.
        """
        num_dossiers = 0
        catalog = getToolByName(self.context, 'portal_catalog')

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        target_repos = data['target_repos']
        num_repos = len(target_repos)

        current_counter_value = self.get_current_counter_value()
        new_counter_value = data['new_counter_value']
        increment = new_counter_value - current_counter_value

        # Check for conflicts
        all_dossiers = catalog(object_provides=IDossierMarker.__identifier__)
        seq_numbers = [brain.sequence_number for brain in all_dossiers 
                       if not brain.sequence_number == MissingValue]
        for seq_no in seq_numbers:
            if new_counter_value < seq_no:
                # There's a potential conflict
                IStatusMessage(self.request).addStatusMessage(
                        _(u"New value %s for sequence number counter" % new_counter_value + \
                          u" will conflict with existing sequence number %s" % seq_no),
                        "error")
                context_url = self.context.absolute_url()
                self.request.response.redirect(context_url)
                return

        logger.info("Adjusting sequence numbers...")
        logger.info("  Current Counter: %s" % current_counter_value)
        logger.info("  New Counter: %s", new_counter_value)
        logger.info("  Increment: %s" % increment)
        logger.info("  Repositories: %s" % target_repos)

        # Adjust the counter
        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        key = DossierSequenceNumberGenerator.key
        sn_counters = ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY)
        increaser = sn_counters[key]
        increaser.set(new_counter_value)

        # Get all dossiers in the specified repositories...
        for repo in target_repos:
            repo_path = '/'.join(repo.getPhysicalPath())
            dossiers = catalog(path=repo_path,
                               object_provides=IDossierMarker.__identifier__)

            # ...and migrate their sequence numbers
            seqNumb = getUtility(ISequenceNumber)
            for brain in dossiers:
                dossier = brain.getObject()
                old_seq_no = seqNumb.get_number(dossier)
                dossier_ann = IAnnotations(dossier)
                dossier_ann['ISequenceNumber.sequence_number'] = old_seq_no + increment
                num_dossiers += 1

        # Redirect back to the front page with a status message
        msg = "Sucessfully adjusted sequence numbers for " + \
              "%s dossiers in %s repositories" % (num_dossiers, num_repos)
        logger.info(msg)
        IStatusMessage(self.request).addStatusMessage(msg, "info")

        context_url = self.context.absolute_url()
        self.request.response.redirect(context_url)


    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
