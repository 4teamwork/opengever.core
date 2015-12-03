from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.browser.sablontemplate import SAMPLE_MEETING_DATA
from opengever.meeting.protocol import ProtocolData
from opengever.testing import FunctionalTestCase


class TestProtocolJsonData(FunctionalTestCase):

    maxDiff = None

    def setUp(self):
        super(TestProtocolJsonData, self).setUp()
        self.proposal = create(
            Builder('proposal_model')
            .having(title=u'Strafbefehl wegen Bauens ohne Bewilligung',
                    initial_position=u'Im Fru\u0308hjahr wurde festgestellt, dass Irgendwer neue Nebenbauten auf einer Liegenschaft erstellt hatte. Auf die mu\u0308ndliche Aufforderung des Ressortvorstehers des Gemeinderates hin reichte er in der Folge ein Baugesuch ein, welches nach Kontrolle durch die Bauverwaltung erga\u0308nzt wurde. Es zeigte sich, dass ein fr\xfcher erstellter Holzschopf durch ein Gartenhaus ersetzt und ein Unterstand fu\u0308r ein Campingfahrzeug an einen fr\xfcher errichteten Holz- und Gera\u0308teschuppen angebaut worden war. Die Baubewilligung konnte nun erteilt werden, wobei die Zustimmung des Departementes Bau, Verkehr und Umwelt eingeholt werden musste, da sich die Bauvorhaben ausserhalb des Baugebietes befinden. Aus dem schriftlich begru\u0308ndeten Nachweis der Notwendigkeit der ausserhalb Baugebiet liegenden Bauten durch den Bauherrn geht hervor, dass das auch als Werkstatt dienende Gartenhaus von seinem in der gleichen Liegenschaft lebenden Sohn erstellt wurde. Er nutzt diese Baute auch.',
                    legal_basis=u'Gegen diesen Strafbefehl k\xf6nnen die Geb\xfcssten innert 20 Tagen seit Er\xf6ffnung beim Gemeinderat schriftlich Einsprache erheben. Die Einsprache hat ein Begehren und eine Begr\xfcndung zu enthalten. In diesem Falle wird eine Einspracheverhandlung vor dem Gemeinderat durchgef\xfchrt, in deren Folge der Gemeinderat einen Entscheid mit Beschwerdem\xf6glichkeit an das Bezirksgericht f\xe4llt.',
                    proposed_action=u'Busse',
                    dossier_reference_number='FD 2.6.8/1',
                    considerations=u'Die Bauten sind eindeutig Baubewilligungspflichtig. Gem\xe4ss \xa7 59 des Baugesetzes bed\xfcrfen alle Bauten und ihre im Hinblick auf die Anliegen der Raumplanung, des Umweltschutzes oder der Baupolizei wesentliche Umgestaltung, Erweiterung oder Zweck\xe4nderung sowie die Beseitigung von Geb\xe4uden der Bewilligung durch den Gemeinderat. Das Bauen ohne Baubewilligung stellt eine strafbare Handlung nach \xa7 160 Baugesetz dar. Strafbar ist die vors\xe4tzliche oder fahrl\xe4ssige Widerhandlung, begangen durch Bauherren, Eigent\xfcmer, sonstige Berechtigte, Projektverfasser, Unternehmer und Bauleiter. Im vorliegenden Fall ist der Straftatbestand durch den Bauherrn und seinen Sohn erf\xfcllt. Aus Gr\xfcnden der Gleichbehandlung mit anderen F\xe4llen ist der Gemeinderat gezwungen, die \xdcbertretung angemessen zu bestrafen.',
                    copy_for_attention=u'Hanspeter',
                    disclose_to=u'Jans\xf6rg',
                    publish_in=u'Tagblatt'))
        self.committee = create(Builder('committee_model'))
        self.member_peter = create(Builder('member'))
        self.member_franz = create(Builder('member')
                                   .having(firstname=u'Franz',
                                           lastname=u'M\xfcller'))
        self.membership_peter = create(Builder('membership').having(
            member=self.member_peter,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role=u'F\xfcrst'))
        self.membership_franz = create(Builder('membership').having(
            member=self.member_franz,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role=None))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            participants=[self.member_peter, self.member_franz],
            other_participants=u'Hans M\xfcller\nHeidi Muster',
            protocol_start_page_number=42,
            meeting_number=11))

        self.agenda_item_proposal = create(
            Builder('agenda_item').having(
                proposal=self.proposal,
                meeting=self.meeting,
                decision=u'Die Bauherren werden gest\xfctzt auf \xa7 160 und in Anwendung von \xa7 162 des Baugesetzes wegen Bauens ohne Baubewilligung gesamthaft bestraft. Der Betrag von je Fr. 1000.-- ist - sofern keine Einsprache erfolgt - innert 30 Tagen der Finanzverwaltung der Gemeinde zu bezahlen.',
                discussion=u'Der Gemeinderat setzt sich geschlossen f\xfcr eine Busse ein.',
                decision_number=1))
        self.agend_item_text = create(
            Builder('agenda_item').having(
                title=u'R\xfccktritt Hans Muster',
                meeting=self.meeting,
                discussion=u'Hans Muster tritt als Gemeinderat zur\xfcck.',
                decision=u'Der Gemeinderat hat den R\xfccktritt genehmigt. Die Neuwahl eines Ersatzmitglieds f\xfcr Hans Muster erfolgt bald. Die Wahlvorschl\xe4ge sind n\xe4chstens bei der Kanzlei einzureichen. Falls ein 2. Wahlgang notwendig werden sollte, wird dieser danach durchgef\xfchrt. Die detaillierten Angaben \xfcber den Eingang der Wahlvorschl\xe4ge usw. sind ab sofort auf der Gemeindehomepage publiziert.',
                decision_number=2))

    def test_protocol_json(self):
        data = ProtocolData(self.meeting).data
        self.assertDictEqual(SAMPLE_MEETING_DATA, data)
