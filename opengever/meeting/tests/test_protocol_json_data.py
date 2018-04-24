from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.model import create_session
from opengever.meeting.browser.sablontemplate import SAMPLE_MEETING_DATA
from opengever.meeting.protocol import ExcerptProtocolData
from opengever.meeting.protocol import ProtocolData
from opengever.testing import FunctionalTestCase


class TestProtocolJsonData(FunctionalTestCase):

    maxDiff = None

    def setUp(self):
        super(TestProtocolJsonData, self).setUp()
        self.root = create(Builder('repository_root'))
        self.folder = create(Builder('repository').titled('Strafwesen'))
        self.dossier = create(
            Builder("dossier").within(self.folder))
        self.doc1 = create(Builder("document")
                           .titled(u'Beweisaufn\xe4hme')
                           .within(self.dossier)
                           .attach_file_containing("lorem ipsum",
                                                   name=u"beweisaufnahme.txt"))
        self.doc2 = create(Builder("document")
                           .titled(u"Strafbefehl")
                           .within(self.dossier))
        self.mail1 = create(Builder("mail")
                            .titled(u"L\xf6rem")
                            .with_message("lorem", filename=u"lorem.eml")
                            .within(self.dossier))
        self.committee = create(Builder('committee')
                                .having(title=u'Gemeinderat'))
        self.proposal = create(
            Builder('proposal')
            .within(self.dossier)
            .having(committee=self.committee,
                    title=u'Strafbefehl wegen Bauens ohne Bewilligung',
                    initial_position=u'<div>Im Fru\u0308hjahr wurde festgestellt, dass Irgendwer neue Nebenbauten auf einer Liegenschaft erstellt hatte. Auf die mu\u0308ndliche Aufforderung des Ressortvorstehers des Gemeinderates hin reichte er in der Folge ein Baugesuch ein, welches nach Kontrolle durch die Bauverwaltung erga\u0308nzt wurde. Es zeigte sich, dass ein fr\xfcher erstellter Holzschopf durch ein Gartenhaus ersetzt und ein Unterstand fu\u0308r ein Campingfahrzeug an einen fr\xfcher errichteten Holz- und Gera\u0308teschuppen angebaut worden war. Die Baubewilligung konnte nun erteilt werden, wobei die Zustimmung des Departementes Bau, Verkehr und Umwelt eingeholt werden musste, da sich die Bauvorhaben ausserhalb des Baugebietes befinden. Aus dem schriftlich begru\u0308ndeten Nachweis der Notwendigkeit der ausserhalb Baugebiet liegenden Bauten durch den Bauherrn geht hervor, dass das auch als Werkstatt dienende Gartenhaus von seinem in der gleichen Liegenschaft lebenden Sohn erstellt wurde. Er nutzt diese Baute auch.</div>',
                    legal_basis=u'<div>Gegen diesen Strafbefehl k\xf6nnen die Geb\xfcssten innert 20 Tagen seit Er\xf6ffnung beim Gemeinderat schriftlich Einsprache erheben. Die Einsprache hat ein Begehren und eine Begr\xfcndung zu enthalten. In diesem Falle wird eine Einspracheverhandlung vor dem Gemeinderat durchgef\xfchrt, in deren Folge der Gemeinderat einen Entscheid mit Beschwerdem\xf6glichkeit an das Bezirksgericht f\xe4llt.</div>',
                    proposed_action=u'<div>Busse</div>',
                    dossier_reference_number=u'FD 2.6.8/1',
                    repository_folder_title=u'Strafwesen',
                    copy_for_attention=u'<div>Hanspeter</div>',
                    disclose_to=u'<div>Jans\xf6rg</div>',
                    decision_draft=u'<div>Der Gemeinderat erstattet Strafanzeige gegen Unbekannt und informiert zudem den Vermieter (Herr. Meier).</div>',
                    publish_in=u'<div>Tagblatt</div>',)
            .relate_to(self.doc1, self.doc2, self.mail1)
            .as_submitted())
        self.proposal_model = self.proposal.load_model()
        self.submitted_proposal = self.proposal_model.resolve_submitted_proposal()
        self.submitted_proposal.considerations = u'<div>Die Bauten sind eindeutig Baubewilligungspflichtig. Gem\xe4ss \xa7 59 des Baugesetzes bed\xfcrfen alle Bauten und ihre im Hinblick auf die Anliegen der Raumplanung, des Umweltschutzes oder der Baupolizei wesentliche Umgestaltung, Erweiterung oder Zweck\xe4nderung sowie die Beseitigung von Geb\xe4uden der Bewilligung durch den Gemeinderat. Das Bauen ohne Baubewilligung stellt eine strafbare Handlung nach \xa7 160 Baugesetz dar. Strafbar ist die vors\xe4tzliche oder fahrl\xe4ssige Widerhandlung, begangen durch Bauherren, Eigent\xfcmer, sonstige Berechtigte, Projektverfasser, Unternehmer und Bauleiter. Im vorliegenden Fall ist der Straftatbestand durch den Bauherrn und seinen Sohn erf\xfcllt. Aus Gr\xfcnden der Gleichbehandlung mit anderen F\xe4llen ist der Gemeinderat gezwungen, die \xdcbertretung angemessen zu bestrafen.</div><ul><li>UL Eintrag</li><li>UL Eintrag<ul><li>UL Einger\xfcckt</li></ul></li></ul>'
        self.member_peter = create(Builder('member'))
        self.member_franz = create(Builder('member')
                                   .having(firstname=u'Franz',
                                           lastname=u'M\xfcller',
                                           email="mueller@example.com"))
        self.member_anna = create(Builder('member')
                                  .having(firstname=u'Anna',
                                          lastname=u'B\xe4nni',
                                          email="baenni@example.com"))
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
        self.membership_anna = create(Builder('membership').having(
            member=self.member_anna,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role=None))
        self.committee_secretary = create(
            Builder('ogds_user')
            .id('committee.secretary')
            .having(firstname=u'C\xf6mmittee', lastname='Secretary', email='committee.secretary@example.com')
            )
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            participants=[self.member_peter,
                          self.member_franz,
                          self.member_anna],
            other_participants=u'Hans M\xfcller\nHeidi Muster',
            protocol_start_page_number=42,
            meeting_number=11,
            presidency=self.member_peter,
            secretary=self.committee_secretary,))

        self.agend_item_text = create(
            Builder('agenda_item').having(
                title=u'R\xfccktritt Hans Muster',
                meeting=self.meeting,
                discussion=u'<div>Hans Muster tritt als Gemeinderat zur\xfcck.</div>',
                decision=u'<div>Der Gemeinderat hat den R\xfccktritt genehmigt. Die Neuwahl eines Ersatzmitglieds f\xfcr Hans Muster erfolgt bald. Die Wahlvorschl\xe4ge sind n\xe4chstens bei der Kanzlei einzureichen. Falls ein 2. Wahlgang notwendig werden sollte, wird dieser danach durchgef\xfchrt. Die detaillierten Angaben \xfcber den Eingang der Wahlvorschl\xe4ge usw. sind ab sofort auf der Gemeindehomepage publiziert.</div>',
                decision_number=2,))

        self.agenda_item_proposal = create(
            Builder('agenda_item').having(
                proposal=self.proposal_model,
                meeting=self.meeting,
                decision=u'<div>Die Bauherren werden gest\xfctzt auf \xa7 160 und in Anwendung von \xa7 162 des Baugesetzes wegen Bauens ohne Baubewilligung gesamthaft bestraft. Der Betrag von je Fr. 1000.-- ist - sofern keine Einsprache erfolgt - innert 30 Tagen der Finanzverwaltung der Gemeinde zu bezahlen.</div><ol><li>Erster Punkt</li><li>Zweiter Punkt<ol><li>Subpunkt</li></ol></li></ol>',
                discussion=u'<div>Der Gemeinderat setzt sich geschlossen f\xfcr eine Busse ein.</div>',
                decision_number=1))

    def test_protocol_json(self):
        data = ProtocolData(self.meeting).data
        self.assertDictEqual(SAMPLE_MEETING_DATA, data)

    def test_add_members_handles_participants_are_no_longer_committee_memberships(self):
        create_session().delete(self.membership_anna)

        self.assertEquals(
            {'members': [{'firstname': 'Anna',
                          'lastname': u'B\xe4nni',
                          'fullname': u'B\xe4nni Anna',
                          'email': 'baenni@example.com',
                         'role': None},
                         {'email': u'mueller@example.com',
                          'firstname': u'Franz',
                          'fullname': u'M\xfcller Franz',
                          'lastname': u'M\xfcller',
                          'role': None},
                         ]},
            ProtocolData(self.meeting).add_members())


class TestExcerptJsonData(FunctionalTestCase):

    maxDiff = None

    def setUp(self):
        super(TestExcerptJsonData, self).setUp()
        self.proposal = create(
            Builder('proposal_model'))
        self.committee = create(Builder('committee_model')
                                .having(title=u'Gemeinderat'))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            protocol_start_page_number=13,
            meeting_number=11,))

    def test_excerpt_json_does_not_contain_start_page(self):
        data = ExcerptProtocolData(self.meeting).data
        self.assertEqual({
            'agenda_items': [],
            'protocol': {'type': u'Protocol-Excerpt'},
            'participants': {'other': [], 'members': []},
            'committee': {'name': u'Gemeinderat'},
            'mandant': {'name': u'Client1'},
            'meeting': {'date': u'Dec 13, 2011',
                        'start_time': u'09:30 AM',
                        'end_time': u'11:45 AM',
                        'number': 11,
                        'location': u'B\xe4rn',
                        }},
            data
        )
