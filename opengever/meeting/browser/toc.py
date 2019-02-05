from opengever.meeting import _
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.exceptions import SablonProcessingFailed
from opengever.meeting.sablon import Sablon
from opengever.meeting.toc.alphabetical import AlphabeticalToc
from opengever.meeting.toc.dossier_refnum import DossierReferenceNumberBasedTOC
from opengever.meeting.toc.repository_refnum import RepositoryReferenceNumberBasedTOC
from opengever.meeting.toc.repository import RepositoryBasedTOC
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Five.browser import BrowserView
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
import json


class DownloadAlphabeticalTOC(BrowserView):

    def __init__(self, context, request):
        super(DownloadAlphabeticalTOC, self).__init__(context, request)
        self.model = context.model

    def __call__(self):
        response = self.request.response
        template = self.model.get_toc_template()
        if not template:
            api.portal.show_message(
                _('msg_no_toc_template',
                  default=u'There is no toc template configured, toc could '
                          'not be generated.'),
                request=self.request,
                type='error')
            response.setHeader('X-ogg-reload-page', "True")
            return

        sablon = Sablon(template)
        try:
            sablon.process(self.get_json_data())
        except SablonProcessingFailed:
            message = _(u'Error while processing Sablon template')
            api.portal.show_message(message, request=self.request, type='error')
            response.setHeader('X-ogg-reload-page', "True")
            return

        filename = self.get_filename().encode('utf-8')
        response.setHeader('X-Theme-Disabled', 'True')
        response.setHeader('Content-Type', MIME_DOCX)
        response.setHeader("Content-Disposition",
                           'attachment; filename="{}"'.format(filename))
        return sablon.file_data

    def get_data(self):
        return AlphabeticalToc(self.model).get_json()

    def get_json_data(self, pretty=False):
        indent = 4 if pretty else None
        return json.dumps(self.get_data(), indent=indent)

    def get_filename(self):
        normalizer = getUtility(IIDNormalizer)
        period_title = normalizer.normalize(self.model.title)
        committee_title = normalizer.normalize(self.model.committee.title)

        return u"{}.docx".format(
            translate(_(u'filename_alphabetical_toc',
                        default=u'Alphabetical Toc ${period} ${committee}',
                        mapping={
                          'period': period_title,
                          'committee': committee_title,
                        }),
                      context=getRequest()))

    def is_manager(self):
        """This condition should reflect is_manager in PeriodsTab.
        """
        return api.user.has_permission('cmf.ManagePortal')

    def as_json(self):
        """Return the table of contents data as JSON."""
        if not self.is_manager():
            raise Unauthorized()
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        return self.get_json_data(pretty=True)


class DownloadRepositoryTOC(DownloadAlphabeticalTOC):

    def get_data(self):
        return RepositoryBasedTOC(self.model).get_json()

    def get_filename(self):
        normalizer = getUtility(IIDNormalizer)
        period_title = normalizer.normalize(self.model.title)
        committee_title = normalizer.normalize(self.model.committee.title)

        return u"{}.docx".format(
            translate(_(u'filename_repository_toc',
                        default=u'Repository Toc ${period} ${committee}',
                        mapping={
                          'period': period_title,
                          'committee': committee_title,
                        }),
                      context=getRequest()))


class DownloadDossierReferenceNumberTOC(DownloadAlphabeticalTOC):

    def get_data(self):
        return DossierReferenceNumberBasedTOC(self.model).get_json()

    def get_filename(self):
        normalizer = getUtility(IIDNormalizer)
        period_title = normalizer.normalize(self.model.title)
        committee_title = normalizer.normalize(self.model.committee.title)

        return u"{}.docx".format(
            translate(_(u'filename_dossier_reference_number_toc',
                        default=u'Dossier Reference Number Toc ${period} ${committee}',
                        mapping={
                          'period': period_title,
                          'committee': committee_title,
                        }),
                      context=getRequest()))


class DownloadRepositoryReferenceNumberTOC(DownloadAlphabeticalTOC):

    def get_data(self):
        return RepositoryReferenceNumberBasedTOC(self.model).get_json()

    def get_filename(self):
        normalizer = getUtility(IIDNormalizer)
        period_title = normalizer.normalize(self.model.title)
        committee_title = normalizer.normalize(self.model.committee.title)

        return u"{}.docx".format(
            translate(_(u'filename_repository_reference_number_toc',
                        default=u'Repository Reference Number Toc ${period} ${committee}',
                        mapping={
                          'period': period_title,
                          'committee': committee_title,
                        }),
                      context=getRequest()))
