from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from opengever.base.model import create_session
from opengever.testing import builders  # keep!
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility


PROPOSED_ACTION_1 = u'''Der Rat stellt der Versammlung den Antrag, der Anstellung von Hans Baumann als Sachbearbeiter mit einem Bescha\u0308ftigungsgrad von 90%, Amtsantritt 01.05.2015, zuzustimmen.'''

INITIAL_POSITION_2 = u'''Der Vorbericht zum Finanzplan wurde erarbeitet und liegt vor.'''

PROPOSED_ACTION_2 = u'''Die Versammlung nimmt vom Finanzplan 2015 - 2019 Kenntnis.'''

INITIAL_POSITION_3 = u'''Der Voranschlag fu\u0308r das Jahr 2015 basiert auf einem unvera\u0308nderten Steuersatz von 0,210 Einheiten und pra\u0308sentiert einen Ausgabenu\u0308berschuss von CHF 613\u2018000.00. Die Einnahmen betragen CHF 8\u2018045\u2018000.00. Dem gegenu\u0308ber stehen Ausgaben von CHF 8\u2018658\u2018000.00.

Der gro\u0308sste Aufwandposten ist wie in den vergangenen Jahren mit CHF 3,050 Mio. die Besoldung der Mitarbeitenden.

Es sind Investitionsvorhaben von CHF 1\u2018288\u2018700.00 geplant.'''

PROPOSED_ACTION_3 = '''Der Kirchgemeinderat stellt der Kirchgemeindeversammlung den Antrag,

1. den Voranschlag 2015 mit einem Ausgabenu\u0308berschuss von CHF 613\u2018000.00 zu genehmigen.

2. den Steuerfuss auf 0.210 Einheiten zu belassen.'''

INITIAL_POSITION_4 = u'''Die Versammlung hat am 6. Juni 2012 einen Verpflichtungskredit von Fr. 144'600.00 fu\u0308r die Revision genehmigt. Nach mehr als 30 Jahren seit der letzten grossen Revision, wo in der Regel alle 20 Jahre sollte durchgefu\u0308hrt werden, hat sich diese aufgedra\u0308ngt.

Wa\u0308hrend den Revisionsarbeiten hat sich herausgestellt, dass zusa\u0308tzlich Arbeiten durchgef\xfchrt werden m\xfcssen.Diese zusa\u0308tzlichen Arbeiten gleichzeitig mit der Revision durchzufu\u0308hren, erschien als sinnvoll. Im letzten Jahr hat deshalb der Besondere Verwalter gestu\u0308tzt auf die einverlangten Offerten einen Nachkredit von rund Fr. 10'000.00 genehmigt. Dies lag betragsma\u0308ssig in seiner Kompetenz.

Wie die Gemeindeverordnung es vorsieht, legen wir Ihnen hiermit die Abrechnung der Revision mit einer Kostenu\u0308berschreitung von Fr. 10'629.15 vor und bitten Sie, davon Kenntnis zu nehmen.
'''

PROPOSED_ACTION_4 = u'''Der Rat stellt der Versammlung den Antrag, die Abrechnung u\u0308ber die Revision mit einer Kostenu\u0308berschreitung von CHF 10\u2018629.15, zur Kenntnis zu nehmen. Der Verpflichtungskredit im Betrag von CHF 144\u2018600.00 wird aufgehoben.'''


class MeetingExampleContentCreator(object):
    """Setup SQL example content.

    Currently it is not possible to do this with ftw.inflator.

    """
    def __init__(self, site):
        self.site = site
        self.db_session = create_session()
        self.setup_builders()
        self.committee_law = self.site['sitzungen']['committee-1']
        self.committee_law_model = self.committee_law.load_model()

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
        self.create_members_and_memberships()
        self.create_meetings()
        self.create_proposals()

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
        self.meeting = create(Builder('meeting').having(
            committee=self.committee_assembly_model,
            location=u'Bern',
            start=datetime.combine(date.today() + timedelta(days=1), time(10, 0)),
            end=datetime.combine(date.today() + timedelta(days=1), time(12, 0))
            )
        )

        # create future meetings
        for delta in [30, 60, 90, 120]:
            create(Builder('meeting').having(
                committee=self.committee_assembly_model,
                location=u'Bern',
                start=datetime.combine(date.today() + timedelta(days=delta),
                                       time(10, 0)),
                end=datetime.combine(date.today() + timedelta(days=delta),
                                     time(12, 0))
                )
            )

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


def block_portlets_for_meetings(site):
    content = site.restrictedTraverse('sitzungen')
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=content)

    # Block inherited context portlets on content
    assignable = getMultiAdapter(
        (content, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def municipality_content_profile_installed(site):
    creator = MeetingExampleContentCreator(site)
    creator.create_content()

    block_portlets_for_meetings(site)
