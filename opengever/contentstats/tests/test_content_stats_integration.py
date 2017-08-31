from ftw.contentstats.interfaces import IStatsKeyFilter
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestContentStatsIntegration(IntegrationTestCase):

    def test_portal_types_filter(self):
        self.login(self.regular_user)
        flt = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            IStatsKeyFilter, name='portal_types')

        # Obviously the core GEVER types should be kept
        self.assertTrue(flt.keep('opengever.document.document'))
        self.assertTrue(flt.keep('opengever.dossier.businesscasedossier'))
        self.assertTrue(flt.keep('opengever.task.task'))

        # As well as ftw.mail
        self.assertTrue(flt.keep('ftw.mail.mail'))

        # These uninteresting top level types should be ignored though
        self.assertFalse(flt.keep('opengever.dossier.templatefolder'))
        self.assertFalse(flt.keep('opengever.repository.repositoryroot'))
        self.assertFalse(flt.keep('opengever.inbox.inbox'))
        self.assertFalse(flt.keep('opengever.inbox.yearfolder'))
        self.assertFalse(flt.keep('opengever.inbox.container'))
        self.assertFalse(flt.keep('opengever.tasktemplates.tasktemplatefolder'))
        self.assertFalse(flt.keep('opengever.contact.contactfolder'))
        self.assertFalse(flt.keep('opengever.meeting.committeecontainer'))

        # Stock Plone types should be skipped as well
        self.assertFalse(flt.keep('ATBooleanCriterion'))
        self.assertFalse(flt.keep('ATCurrentAuthorCriterion'))
        self.assertFalse(flt.keep('ATDateCriteria'))
        self.assertFalse(flt.keep('ATDateRangeCriterion'))
        self.assertFalse(flt.keep('ATListCriterion'))
        self.assertFalse(flt.keep('ATPathCriterion'))
        self.assertFalse(flt.keep('ATRelativePathCriterion'))
        self.assertFalse(flt.keep('ATPortalTypeCriterion'))
        self.assertFalse(flt.keep('ATReferenceCriterion'))
        self.assertFalse(flt.keep('ATSelectionCriterion'))
        self.assertFalse(flt.keep('ATSimpleIntCriterion'))
        self.assertFalse(flt.keep('ATSimpleStringCriterion'))
        self.assertFalse(flt.keep('ATSortCriterion'))
        self.assertFalse(flt.keep('Discussion Item'))
        self.assertFalse(flt.keep('Document'))
        self.assertFalse(flt.keep('Event'))
        self.assertFalse(flt.keep('File'))
        self.assertFalse(flt.keep('Folder'))
        self.assertFalse(flt.keep('Image'))
        self.assertFalse(flt.keep('Link'))
        self.assertFalse(flt.keep('News Item'))
        self.assertFalse(flt.keep('Plone Site'))
        self.assertFalse(flt.keep('TempFolder'))
        self.assertFalse(flt.keep('Topic'))
        self.assertFalse(flt.keep('Collection'))

        # But any potential future type in opengever.* should be kept
        self.assertTrue(flt.keep('opengever.doesnt.exist.just.yet'))
