from ftw.upgrade import UpgradeStep
from plone import api
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import queryMultiAdapter
from zope.component import queryUtility
import logging
import re


MAX_COLUMNS = 4

NEW_URL = u'https://feedback.onegovgever.ch'
OLD_URL_RE = re.compile(u'http[s]?://feedback.onegov.ch', flags=re.IGNORECASE)

log = logging.getLogger('ftw.upgrade')


class UpdateFeedbackLinkInFooter(UpgradeStep):
    """Updates any occurrences of the old URL for the feedback forum with
    the new one in all ftw.footer portlets on the site root.
    """

    def __call__(self):
        # ftw.footer was removed
        # assignments = self._get_footer_portlet_assignments()
        # for assignment in assignments:
        #     self._update_link_if_necessary(assignment)
        pass

    def _update_link_if_necessary(self, assignment):
        markup, name = assignment.text, assignment.__name__

        if re.search(OLD_URL_RE, markup):
            assignment.text = re.sub(OLD_URL_RE, NEW_URL, markup)
            log.info("Updated feedback link for footer column %r" % name)

    def _get_footer_portlet_assignments(self):
        site = api.portal.get()
        for col_num in range(1, MAX_COLUMNS + 1):
            manager_name = 'ftw.footer.column%s' % col_num

            assignments = self._get_all_portlet_assignments(
                site, manager_name)

            for assignment in assignments:
                yield assignment

    def _get_all_portlet_assignments(self, context, manager_name):
        manager = queryUtility(
            IPortletManager, context=context, name=manager_name,)

        mapping = queryMultiAdapter(
            (context, manager), IPortletAssignmentMapping, default={})

        for name, assignment in mapping.items():
            yield assignment
