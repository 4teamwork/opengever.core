from datetime import date
from opengever.base.interfaces import IReferenceNumber
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.ogds.base.utils import get_current_admin_unit


def format_date(value):
    if isinstance(value, date):
        return value.strftime("%Y-%M-%d")
    return None


class DispositionDossierCSVReporter(object):

    def __init__(self, dossiers):
        self.dossiers = dossiers

    def __call__(self):
        lines = []
        lines.append([attr.get('label') for attr in self.attributes()])

        for dossier in self.dossiers:
            values = []
            for attribute in self.attributes():
                if attribute.get('binding_id'):
                    value = getattr(dossier.binding(), attribute.get('binding_id'))
                else:
                    value = attribute.get('value')(dossier)

                value = value if value else u''
                values.append(value)

            lines.append(values)

        return lines

    def attributes(self):
        return [
            {
                'label': u'id',
                'binding_id': 'id'
            },
            {
                'label': u'Mandant',
                'value': self.admin_unit_label
            },
            {
                'label': u'Ordnungsystem_Version',
                'value': self.repository_version
            },
            {
                'label': u'Ordnungssystem_Pfad',
                'value': self.repository_path
            },
            {
                'label': u'Dossier_Titel',
                'value': self.dossier_title
            },
            {
                'label': u'entstehungszeitraum_von',
                'value': self.entstehtungszeitraum_von
            },
            {
                'label': u'entstehungszeitraum_bis',
                'value': self.entstehtungszeitraum_bis
            },
            {
                'label': u'klassifizierungskategorie',
                'binding_id': 'klassifizierungskategorie'
            },
            {
                'label': u'datenschutz',
                'binding_id': 'datenschutz'
            },
            {
                'label': u'oeffentlichkeitsstatus',
                'binding_id': 'oeffentlichkeitsstatus'
            },
            {
                'label': u'aktenzeichen',
                'binding_id': 'aktenzeichen'
            },
            {
                'label': u'eroeffnungsdatum',
                'value': self.start_date
            },
            {
                'label': u'abschlussdatum',
                'value': self.end_date
            },
            {
                'label': u'schutzfrist',
                'binding_id': 'schutzfrist'
            },
            {
                'label': u'Ablage_Pr\xe4fix',
                'value': self.filing_prefix
            },
            {
                'label': u'Ablage_Nr',
                'value': self.filing_number
            },
            {
                'label': u'Beschreibung',
                'value': self.description
            }
        ]

    def binding_id(self, dossier):
        return dossier.binding().id

    def admin_unit_label(self, dossier):
        return get_current_admin_unit().label()

    def repository_version(self, dossier):
        return dossier.parents()[0].version

    def repository_path(self, dossier):
        # skip dossier itself
        return u'/'.join(
            [parent.Title().decode('utf-8') for parent in dossier.parents()[:-1]])

    def dossier_title(self, dossier):
        return dossier.obj.title

    def start_date(self, dossier):
        value = dossier.binding().eroeffnungsdatum.datum
        if isinstance(value, date):
            return value.strftime("%Y-%M-%d")
        return None

    def end_date(self, dossier):
        value = dossier.binding().abschlussdatum.datum
        if isinstance(value, date):
            return value.strftime("%Y-%M-%d")
        return None

    def entstehtungszeitraum_von(self, dossier):
        value = dossier.binding().entstehungszeitraum.von.datum
        if isinstance(value, date):
            return value.strftime("%Y-%M-%d")
        return None

    def entstehtungszeitraum_bis(self, dossier):
        value = dossier.binding().entstehungszeitraum.bis.datum
        if isinstance(value, date):
            return value.strftime("%Y-%M-%d")
        return None

    def filing_prefix(self, dossier):
        return dossier.obj.filing_prefix

    def filing_number(self, dossier):
        if IFilingNumberMarker.providedBy(dossier.obj):
            return IFilingNumber(dossier.obj).filing_no

    def description(self, dossier):
        return dossier.obj.description


class DispositionDocumentCSVReporter(object):

    fieldnames = [
        'dossier_id',
        'document_id',
        'laufnummer',
        'sip_folder_name',
        'sip_file_name',
        'document_title',
        'erscheinungsform',
        'registrierdatum',
        'entstehtungszeitraum_von',
        'entstehtungszeitraum_bis',
        'klassifizierungskategorie',
        'datenschutz',
        'oeffentlichkeitsstatus',
        'oeffentlichkeitsstatusBegruendung',
        'dateiRef',
        'originalName',
        'pruefalgorithmus',
        'pruefsumme',
        'dokumentdatum',
        'beschreibung',
        'autor',
        'aktenzeichen']

    def __init__(self, dossiers):
        self.dossiers = dossiers

    def __call__(self):
        lines = []
        for dossier in self.dossiers:
            for key, document in dossier.documents.items():
                for file_ in document.files:
                    doc_binding = document.binding()
                    lines.append({
                        'dossier_id': dossier.binding().id,
                        'document_id': doc_binding.id,
                        'laufnummer': document.obj.get_sequence_number(),
                        'sip_folder_name': dossier.folder.name,
                        'sip_file_name': file_.binding().name,
                        'document_title': document.obj.Title(),
                        'erscheinungsform': doc_binding.erscheinungsform,
                        'registrierdatum': format_date(doc_binding.registrierdatum.datum),
                        'entstehtungszeitraum_von': format_date(
                            doc_binding.entstehungszeitraum.von.datum),
                        'entstehtungszeitraum_bis': format_date(
                            doc_binding.entstehungszeitraum.bis.datum),
                        'klassifizierungskategorie': doc_binding.klassifizierungskategorie,
                        'datenschutz': doc_binding.datenschutz,
                        'oeffentlichkeitsstatus': doc_binding.oeffentlichkeitsstatus,
                        'oeffentlichkeitsstatusBegruendung': doc_binding.oeffentlichkeitsstatusBegruendung,
                        'dateiRef': file_.binding().id,
                        'originalName': file_.binding().originalName,
                        'pruefalgorithmus': file_.binding().pruefalgorithmus,
                        'pruefsumme': file_.binding().pruefsumme,
                        'dokumentdatum': format_date(document.obj.document_date),
                        'beschreibung': document.obj.description,
                        'autor': document.obj.document_author,
                        'aktenzeichen': IReferenceNumber(document.obj).get_number(),
                    })

        return lines
