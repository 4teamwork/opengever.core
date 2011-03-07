from five import grok
from logging import getLogger

from opengever.base import _
from opengever.base.interfaces import ISequenceNumber
from opengever.base.sequence import SEQUENCE_NUMBER_ANNOTATION_KEY
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.sequence import DossierSequenceNumberGenerator

from plone.directives import form
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility


logger = getLogger('opengever.base')

class IAdjustSequenceNumbersSchema(form.Schema):

    new_counter_value = schema.Int(
            title=_(u"Enter the new value for the dossier sequence number counter"),
            min=0,
            required=True
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

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        current_counter_value = self.get_current_counter_value()
        new_counter_value = data['new_counter_value']
        increment = new_counter_value - current_counter_value

        logger.info("Adjusting sequence numbers...")
        logger.info("  Current Counter: %s" % current_counter_value)
        logger.info("  New Counter: ", new_counter_value)
        logger.info("  Increment: %s" % increment)

        # Adjust the counter
        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        key = DossierSequenceNumberGenerator.key
        sn_counters = ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY)
        increaser = sn_counters[key]
        increaser.set(new_counter_value)

        # Get all dossiers in the specified repository...
        catalog = getToolByName(self.context, 'portal_catalog')
        repo_id = "ordnungssystem"
        repo_path = '/'.join(portal.getPhysicalPath() + (repo_id,))
        dossiers = catalog(path=repo_path,
                           object_provides=IDossierMarker.__identifier__)
        num_dossiers = len(dossiers)

        # ...and migrate their sequence numbers
        seqNumb = getUtility(ISequenceNumber)
        for brain in dossiers:
            dossier = brain.getObject()
            old_seq_no = seqNumb.get_number(dossier)
            dossier_ann = IAnnotations(dossier)
            dossier_ann['ISequenceNumber.sequence_number'] = old_seq_no + increment

        # Redirect back to the front page with a status message
        logger.info("Sucessfully adjusted sequence numbers for %s dossiers." % num_dossiers)
        IStatusMessage(self.request).addStatusMessage(
                _(u"Sequence Number Counter adjusted - %s dossiers migrated" % num_dossiers), 
                "info")

        context_url = self.context.absolute_url()
        self.request.response.redirect(context_url)


    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
