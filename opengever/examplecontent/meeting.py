from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from opengever.base.model import create_session
from opengever.testing import assets
from opengever.testing import builders  # noqa
from plone import api
import pytz


class MeetingExampleContentCreator(object):
    """Setup SQL example content.

    Currently it is not possible to do this with ftw.inflator.

    """
    tz = pytz.timezone('Europe/Zurich')

    def __init__(self, site):
        self.site = site
        self.db_session = create_session()
        self.setup_builders()
        self.committee_law = self.site['sitzungen']['committee-1']
        self.committee_law_model = self.committee_law.load_model()

        self.committee_accounting = self.site['sitzungen']['committee-2']
        self.committee_accounting_model = self.committee_accounting.load_model()

        self.committee_assembly = self.site['sitzungen']['committee-3']
        self.committee_assembly_model = self.committee_assembly.load_model()

        self.committee_evil = self.site['sitzungen']['evil-committee-1']
        self.committee_evil_model = self.committee_evil.load_model()

        self.dossier_taxes_1 = self.site.restrictedTraverse(
            'ordnungssystem/ressourcen-und-support/finanzen/planung/finanzplanung/dossier-5')
        self.dossier_taxes_2 = self.site.restrictedTraverse(
            'ordnungssystem/ressourcen-und-support/finanzen/planung/finanzplanung/dossier-6')
        self.dossier_equipment = self.site.restrictedTraverse(
            'ordnungssystem/ressourcen-und-support/finanzen/planung/investitionsplanung/dossier-7')

        self.dossier_baufrau = self.site.restrictedTraverse(
            'ordnungssystem/ressourcen-und-support/personal/personalrekrutierung/dossier-5')
        self.dossier_laws_1 = self.site.restrictedTraverse(
            'ordnungssystem/bevoelkerung-und-sicherheit/einwohnerkontrolle/dossier-1')
        self.dossier_laws_2 = self.site.restrictedTraverse(
            'ordnungssystem/bevoelkerung-und-sicherheit/einwohnerkontrolle/dossier-2')
        self.repository_folder_meeting_word = self.site.restrictedTraverse(
            'ordnungssystem/fuehrung/gemeinderecht')

        self.document_baufrau_1 = self.dossier_baufrau['document-2']
        self.document_baufrau_2 = self.dossier_baufrau['document-3']
        self.document_baufrau_3 = self.dossier_baufrau['document-4']

        self.document_taxes_1 = self.dossier_taxes_1['document-4']
        self.document_taxes_2 = self.dossier_taxes_1['document-5']
        self.document_taxes_3 = self.dossier_taxes_2['document-6']

        self.document_laws_1 = self.dossier_laws_1['document-4']
        self.document_laws_2 = self.dossier_laws_1['document-5']

        self.document_equipment_1 = self.dossier_equipment['document-7']
        self.document_equipment_2 = self.dossier_equipment['document-8']

    def setup_builders(self):
        session.current_session = session.BuilderSession()
        session.current_session.session = self.db_session

    def create_content(self):
        self.create_periods()
        self.create_members_and_memberships()
        self.create_meetings_word()
        self.create_proposals_word()

    def create_periods(self):
        create(Builder('period').having(
            start=date(2016, 1, 1),
            end=date(2016, 12, 31)).within(self.committee_law))
        create(Builder('period').having(
            start=date(2016, 1, 1),
            end=date(2016, 12, 31)).within(self.committee_accounting))
        create(Builder('period').having(
            start=date(2016, 1, 1),
            end=date(2016, 12, 31)).within(self.committee_assembly))
        create(Builder('period').having(
            start=date(2016, 1, 1),
            end=date(2016, 12, 31)).within(self.committee_evil))

    def create_members_and_memberships(self):
        peter = create(Builder('member')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        hans = create(Builder('member')
                      .having(firstname=u'Hans', lastname=u'Meier'))

        for committee in [self.committee_law_model,
                          self.committee_assembly_model]:
            create(Builder('membership')
                   .having(committee=committee,
                           member=peter,
                           date_from=date.today(),
                           date_to=date.today() + timedelta(days=512)))

            create(Builder('membership')
                   .having(committee=committee,
                           member=hans,
                           date_from=date.today(),
                           date_to=date.today() + timedelta(days=512)))

    def create_meetings_word(self):
        self.dossier_word, self.meeting_word = self.create_meeting_word(delta=1)

        # create future meetings
        for delta in [30, 60, 90, 120]:
            self.create_meeting_word(delta=delta)

    def create_meeting_word(self, delta):
        start = self.tz.localize(
            datetime.combine(date.today() + timedelta(days=delta), time(10, 0)))
        end = self.tz.localize(
            datetime.combine(date.today() + timedelta(days=delta), time(12, 0)))
        title = u"Kommission f\xfcr Rechtsfragen, {}".format(
            api.portal.get_localized_time(datetime=start))

        dossier = create(Builder('meeting_dossier')
                         .having(
                             responsible=u'lukas.graf',
                             title=u'Meeting {}'.format(
                                 api.portal.get_localized_time(start)),)
                         .within(self.repository_folder_meeting_word))
        meeting = create(Builder('meeting')
                         .having(title=title,
                                 committee=self.committee_law_model,
                                 location=u'Bern',
                                 start=start,
                                 end=end,)
                         .link_with(dossier))
        return dossier, meeting

    def create_proposals_word(self):
        proposal1 = create(
            Builder('proposal')
            .within(self.dossier_baufrau)
            .having(committee=self.committee_law_model,
                    title=u'Genehmigung der Anstellung von Hannah Baufrau als '
                          u'Sachbearbeiterin einem Besch\xe4ftigungsgrad von 90%')
            .relate_to(self.document_baufrau_1,
                       self.document_baufrau_2,
                       self.document_baufrau_3)
            .with_proposal_file(assets.load('vertragsentwurf.docx'))
            .as_submitted())
        self.meeting_word.schedule_proposal(proposal1.load_model())

        self.meeting_word.schedule_ad_hoc(
            u'Genehmigung der Bestellung von Hannah Baufrau als Sachbearbeterin '
            u'einem Besch\xe4ftigungsgrad von 90%')

        proposal2 = create(
            Builder('proposal')
            .within(self.dossier_laws_1)
            .having(committee=self.committee_law_model,
                    title=u'Revision der Rechtslage f\xfcr eine Liberalisierung')
            .relate_to(self.document_laws_1, self.document_laws_2)
            .with_proposal_file(assets.load('vertragsentwurf.docx')))

        self.meeting_word.schedule_ad_hoc(
            u'Revision der Linkslage f\xfcr eine Liberalisierung')
