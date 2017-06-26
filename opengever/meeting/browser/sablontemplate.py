from five import grok
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.sablon import Sablon
from opengever.meeting.sablontemplate import ISablonTemplate
import json


SAMPLE_MEETING_DATA = {
    '_sablon': {'properties': {'start_page_number': 42}},
    'agenda_items': [{
        'description': u'Strafbefehl wegen Bauens ohne Bewilligung',
        'dossier_reference_number': 'FD 2.6.8/1',
        'repository_folder_title': u'Strafwesen',
        'html:considerations': u'<div>Die Bauten sind eindeutig Baubewilligungspflichtig. Gem\xe4ss \xa7 59 des Baugesetzes bed\xfcrfen alle Bauten und ihre im Hinblick auf die Anliegen der Raumplanung, des Umweltschutzes oder der Baupolizei wesentliche Umgestaltung, Erweiterung oder Zweck\xe4nderung sowie die Beseitigung von Geb\xe4uden der Bewilligung durch den Gemeinderat. Das Bauen ohne Baubewilligung stellt eine strafbare Handlung nach \xa7 160 Baugesetz dar. Strafbar ist die vors\xe4tzliche oder fahrl\xe4ssige Widerhandlung, begangen durch Bauherren, Eigent\xfcmer, sonstige Berechtigte, Projektverfasser, Unternehmer und Bauleiter. Im vorliegenden Fall ist der Straftatbestand durch den Bauherrn und seinen Sohn erf\xfcllt. Aus Gr\xfcnden der Gleichbehandlung mit anderen F\xe4llen ist der Gemeinderat gezwungen, die \xdcbertretung angemessen zu bestrafen.</div><ul><li>UL Eintrag</li><li>UL Eintrag<ul><li>UL Einger\xfcckt</li></ul></li></ul>',
        'html:decision_draft':u'<div>Der Gemeinderat erstattet Strafanzeige gegen Unbekannt und informiert zudem den Vermieter (Herr. Meier).</div>',
        'html:decision': u'<div>Die Bauherren werden gest\xfctzt auf \xa7 160 und in Anwendung von \xa7 162 des Baugesetzes wegen Bauens ohne Baubewilligung gesamthaft bestraft. Der Betrag von je Fr. 1000.-- ist - sofern keine Einsprache erfolgt - innert 30 Tagen der Finanzverwaltung der Gemeinde zu bezahlen.</div><ol><li>Erster Punkt</li><li>Zweiter Punkt<ol><li>Subpunkt</li></ol></li></ol>',
        'html:discussion': u'<div>Der Gemeinderat setzt sich geschlossen f\xfcr eine Busse ein.</div>',
        'html:initial_position': u'<div>Im Fru\u0308hjahr wurde festgestellt, dass Irgendwer neue Nebenbauten auf einer Liegenschaft erstellt hatte. Auf die mu\u0308ndliche Aufforderung des Ressortvorstehers des Gemeinderates hin reichte er in der Folge ein Baugesuch ein, welches nach Kontrolle durch die Bauverwaltung erga\u0308nzt wurde. Es zeigte sich, dass ein fr\xfcher erstellter Holzschopf durch ein Gartenhaus ersetzt und ein Unterstand fu\u0308r ein Campingfahrzeug an einen fr\xfcher errichteten Holz- und Gera\u0308teschuppen angebaut worden war. Die Baubewilligung konnte nun erteilt werden, wobei die Zustimmung des Departementes Bau, Verkehr und Umwelt eingeholt werden musste, da sich die Bauvorhaben ausserhalb des Baugebietes befinden. Aus dem schriftlich begru\u0308ndeten Nachweis der Notwendigkeit der ausserhalb Baugebiet liegenden Bauten durch den Bauherrn geht hervor, dass das auch als Werkstatt dienende Gartenhaus von seinem in der gleichen Liegenschaft lebenden Sohn erstellt wurde. Er nutzt diese Baute auch.</div>',
        'html:legal_basis': u'<div>Gegen diesen Strafbefehl k\xf6nnen die Geb\xfcssten innert 20 Tagen seit Er\xf6ffnung beim Gemeinderat schriftlich Einsprache erheben. Die Einsprache hat ein Begehren und eine Begr\xfcndung zu enthalten. In diesem Falle wird eine Einspracheverhandlung vor dem Gemeinderat durchgef\xfchrt, in deren Folge der Gemeinderat einen Entscheid mit Beschwerdem\xf6glichkeit an das Bezirksgericht f\xe4llt.</div>',
        'html:proposed_action': u'<div>Busse</div>',
        'html:copy_for_attention': u'<div>Hanspeter</div>',
        'html:disclose_to': u'<div>Jans\xf6rg</div>',
        'html:publish_in': u'<div>Tagblatt</div>',
        'number': '1.',
        'title': u'Strafbefehl wegen Bauens ohne Bewilligung',
        'is_paragraph': False,
        'decision_number': 1,
        'attachments': [{
            "title": "Beweisaufn\xc3\xa4hme",
            "filename": u"beweisaufna-hme.txt"
            }, {
            "title": "Strafbefehl"
            }, {
            "title": u"L\xf6rem",
            "filename": u"lorem.eml"
        }]
    }, {
        'description': u'R\xfccktritt Hans Muster',
        'dossier_reference_number': None,
        'repository_folder_title': None,
        'html:considerations': None,
        'html:decision_draft': None,
        'html:decision': u'<div>Der Gemeinderat hat den R\xfccktritt genehmigt. Die Neuwahl eines Ersatzmitglieds f\xfcr Hans Muster erfolgt bald. Die Wahlvorschl\xe4ge sind n\xe4chstens bei der Kanzlei einzureichen. Falls ein 2. Wahlgang notwendig werden sollte, wird dieser danach durchgef\xfchrt. Die detaillierten Angaben \xfcber den Eingang der Wahlvorschl\xe4ge usw. sind ab sofort auf der Gemeindehomepage publiziert.</div>',
        'html:discussion': u'<div>Hans Muster tritt als Gemeinderat zur\xfcck.</div>',
        'html:initial_position': None,
        'html:legal_basis': None,
        'html:proposed_action': None,
        'html:copy_for_attention': None,
        'html:disclose_to': None,
        'html:publish_in': None,
        'number': '2.',
        'title': u'R\xfccktritt Hans Muster',
        'is_paragraph': False,
        'decision_number': 2}],
    'mandant': {'name': u'Client1'},
    'meeting': {'date': u'Dec 13, 2011',
                'end_time': u'11:45 AM',
                'start_time': u'09:30 AM',
                'number': 11,
                'location': u'B\xe4rn'},
    'committee': {'name': u'Gemeinderat'},
    'participants': {
        'presidency': {'fullname': u'M\xfcller Peter',
                       'email': None,
                       'role': u'F\xfcrst'},
        'secretary': {'fullname': u'M\xfcller Franz',
                      'email': 'mueller@example.com',
                      'role': None},
        'members': [
                    {'fullname': u'B\xe4nni Anna',
                     'role': None,
                     'email': u'baenni@example.com'},
                    {'fullname': u'M\xfcller Franz',
                     'role': None,
                     'email': u'mueller@example.com'},
                    {'fullname': u'M\xfcller Peter',
                     'role': u'F\xfcrst',
                     'email': None},
                    ],
        'other': [u'Hans M\xfcller', u'Heidi Muster']},
    'protocol': {'type': u'Protocol'}}


class FillMeetingTemplate(grok.View):
    """View to fill a template with sample data for a meeting."""

    grok.name('fill_meeting_template')
    grok.context(ISablonTemplate)
    grok.require('cmf.ManagePortal')

    def render(self):
        sablon = Sablon(self.context)
        sablon.process(json.dumps(SAMPLE_MEETING_DATA))
        assert sablon.is_processed_successfully(), sablon.stderr

        response = self.request.response
        response.setHeader('X-Theme-Disabled', 'True')
        response.setHeader('Content-Type', MIME_DOCX)
        response.setHeader("Content-Disposition",
                           'attachment; filename="{}"'.format('template.docx'))
        return sablon.file_data
