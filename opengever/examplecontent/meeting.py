from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from opengever.base.model import create_session
from opengever.testing import builders  # keep!
from plone import api
import pytz

# Please pyflakes
builders

PROPOSED_ACTION_1 = (
    u'Der Rat stellt der Versammlung den Antrag, der Anstellung von Hans '
    u'Baumann als Sachbearbeiter mit einem Bescha\u0308ftigungsgrad von 90%, '
    u'Amtsantritt 01.05.2015, zuzustimmen.'
)

INITIAL_POSITION_2 = u'Der Vorbericht zum Finanzplan wurde erarbeitet und liegt vor.'

PROPOSED_ACTION_2 = u'Die Versammlung nimmt vom Finanzplan 2015 - 2019 Kenntnis.'

INITIAL_POSITION_3 = (
    u'Der Voranschlag fu\u0308r das Jahr 2015 basiert auf einem '
    u'unvera\u0308nderten Steuersatz von 0,210 Einheiten und pra\u0308sentiert '
    u'einen Ausgabenu\u0308berschuss von CHF 613\u2018000.00. Die Einnahmen '
    u'betragen CHF 8\u2018045\u2018000.00. Dem gegenu\u0308ber stehen Ausgaben '
    u'von CHF 8\u2018658\u2018000.00.\n\n Der gro\u0308sste Aufwandposten ist '
    u'wie in den vergangenen Jahren mit CHF 3,050 Mio. die Besoldung der '
    u'Mitarbeitenden.\n\nEs sind Investitionsvorhaben von CHF '
    u'1\u2018288\u2018700.00 geplant.'
)

PROPOSED_ACTION_3 = (
    u'Der Kirchgemeinderat stellt der Kirchgemeindeversammlung den Antrag,\n'
    u'1. den Voranschlag 2015 mit einem Ausgabenu\u0308berschuss von CHF '
    u'613\u2018000.00 zu genehmigen.\n2. den Steuerfuss auf 0.210 Einheiten zu belassen.'
)

INITIAL_POSITION_4 = (
    u'Die Versammlung hat am 6. Juni 2012 einen Verpflichtungskredit von Fr. '
    u'144\u2018600.00 fu\u0308r die Revision genehmigt. Nach mehr als 30 '
    u'Jahren seit der letzten grossen Revision, wo in der Regel alle 20 Jahre '
    u'sollte durchgefu\u0308hrt werden, hat sich diese aufgedra\u0308ngt.\n\n'
    u'Wa\u0308hrend den Revisionsarbeiten hat sich herausgestellt, dass '
    u'zusa\u0308tzlich Arbeiten durchgef\xfchrt werden m\xfcssen. Diese '
    u'zusa\u0308tzlichen Arbeiten gleichzeitig mit der Revision '
    u'durchzufu\u0308hren, erschien als sinnvoll. Im letzten Jahr hat deshalb '
    u'der Besondere Verwalter gestu\u0308tzt auf die einverlangten Offerten '
    u'einen Nachkredit von rund Fr. 10\'000.00 genehmigt. Dies lag '
    u'betragsma\u0308ssig in seiner Kompetenz.\n\n'
    u'Wie die Gemeindeverordnung es vorsieht, legen wir Ihnen hiermit die '
    u'Abrechnung der Revision mit einer Kostenu\u0308berschreitung von Fr. '
    u'10\'629.15 vor und bitten Sie, davon Kenntnis zu nehmen.'
)

PROPOSED_ACTION_4 = (
    u'Der Rat stellt der Versammlung den Antrag, die Abrechnung u\u0308ber die'
    u'Revision mit einer Kostenu\u0308berschreitung von CHF 10\u2018629.15, '
    u'zur Kenntnis zu nehmen. Der Verpflichtungskredit im Betrag von CHF '
    u'144\u2018600.00 wird aufgehoben.'
)


class ExampleContentCreator(object):
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

        self.dossier_baumann = self.site.restrictedTraverse(
            'ordnungssystem/ressourcen-und-support/personal/personalrekrutierung/dossier-4')
        self.dossier_taxes_1 = self.site.restrictedTraverse(
            'ordnungssystem/ressourcen-und-support/finanzen/planung/finanzplanung/dossier-5')
        self.dossier_taxes_2 = self.site.restrictedTraverse(
            'ordnungssystem/ressourcen-und-support/finanzen/planung/finanzplanung/dossier-6')
        self.dossier_equipment = self.site.restrictedTraverse(
            'ordnungssystem/ressourcen-und-support/finanzen/planung/investitionsplanung/dossier-7')
        self.repository_folder_meeting = self.site.restrictedTraverse(
            'ordnungssystem/fuehrung/gemeindeversammlung-gemeindeparlament-legislative/versammlungen-sitzungen')

        self.document_baumann_1 = self.dossier_baumann['document-2']
        self.document_baumann_2 = self.dossier_baumann['document-3']

        self.document_taxes_1 = self.dossier_taxes_1['document-4']
        self.document_taxes_2 = self.dossier_taxes_1['document-5']
        self.document_taxes_3 = self.dossier_taxes_2['document-6']

        self.document_equipment_1 = self.dossier_equipment['document-7']
        self.document_equipment_2 = self.dossier_equipment['document-8']

    def setup_builders(self):
        session.current_session = session.BuilderSession()
        session.current_session.session = self.db_session

    def create_content(self):
        self.create_periods()
        self.create_members_and_memberships()
        self.create_meetings()
        self.create_proposals()

    def create_periods(self):
        create(Builder('period').having(
            date_from=date(2016, 1, 1),
            date_to=date(2016, 12, 31),
            committee=self.committee_law_model))
        create(Builder('period').having(
            date_from=date(2016, 1, 1),
            date_to=date(2016, 12, 31),
            committee=self.committee_accounting_model))
        create(Builder('period').having(
            date_from=date(2016, 1, 1),
            date_to=date(2016, 12, 31),
            committee=self.committee_assembly_model))

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

    def create_meetings(self):
        self.dossier, self.meeting = self.create_meeting(delta=1)

        # create future meetings
        for delta in [30, 60, 90, 120]:
            self.create_meeting(delta=delta)

    def create_meeting(self, delta):
        start = self.tz.localize(
            datetime.combine(date.today() + timedelta(days=delta), time(10, 0)))
        end = self.tz.localize(
            datetime.combine(date.today() + timedelta(days=delta), time(12, 0)))
        title = "Gemeindeversammlung, {}".format(
            api.portal.get_localized_time(datetime=start))

        dossier = create(Builder('meeting_dossier')
                         .having(title=u'Meeting {}'.format(
                             api.portal.get_localized_time(start)),)
                         .within(self.repository_folder_meeting))
        meeting = create(Builder('meeting')
                         .having(title=title,
                                 committee=self.committee_assembly_model,
                                 location=u'Bern',
                                 start=start,
                                 end=end,)
                         .link_with(dossier))
        return dossier, meeting

    def create_proposals(self):
        proposal1 = create(
            Builder('proposal')
            .within(self.dossier_baumann)
            .having(committee=self.committee_assembly_model,
                    title=u'Genehmigung der Anstellung von Hans Baumann als '
                          u'Sachbearbeiter einem Besch\xe4ftigungsgrad von 90%',
                    proposed_action=PROPOSED_ACTION_1)
            .relate_to(self.document_baumann_1, self.document_baumann_2)
            .as_submitted())
        self.meeting.schedule_proposal(proposal1.load_model())

        proposal2 = create(
            Builder('proposal')
            .within(self.dossier_taxes_1)
            .having(committee=self.committee_assembly_model,
                    title=u'Finanzplanung 2015 - 2019',
                    initial_position=INITIAL_POSITION_2,
                    proposed_action=PROPOSED_ACTION_2)
            .relate_to(self.document_taxes_1, self.document_taxes_2)
            .as_submitted())
        self.meeting.schedule_proposal(proposal2.load_model())

        proposal3 = create(
            Builder('proposal')
            .within(self.dossier_taxes_2)
            .having(committee=self.committee_assembly_model,
                    title=u'Voranschlag 2015 und Festsetzung der Steueranlage',
                    initial_position=INITIAL_POSITION_3,
                    proposed_action=PROPOSED_ACTION_3)
            .relate_to(self.document_taxes_3)
            .as_submitted())
        self.meeting.schedule_proposal(proposal3.load_model())

        proposal4 = create(
            Builder('proposal')
            .within(self.dossier_taxes_2)
            .having(committee=self.committee_assembly_model,
                    title=u'Schlussabrechnung Revision, Liebefeld',
                    initial_position=INITIAL_POSITION_4,
                    proposed_action=PROPOSED_ACTION_4)
            .relate_to(self.document_equipment_1, self.document_equipment_2)
            .as_submitted())
        self.meeting.schedule_proposal(proposal4.load_model())
