from datetime import date
from opengever.base.interfaces import IReferenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.ogds.base.utils import get_current_admin_unit


def format_date(value):
    if isinstance(value, date):
        return value.strftime("%Y-%M-%d")
    return None


class DispositionDossierCSVReporter(object):

    fieldnames = [
        'dossier_id',
        'Mandant',
        'Ordnungsystem_Version',
        'Ordnungssystem_Pfad',
        'Dossier_Titel',
        'entstehungszeitraum_von',
        'entstehungszeitraum_bis',
        'klassifizierungskategorie',
        'datenschutz',
        'oeffentlichkeitsstatus',
        'aktenzeichen',
        'eroeffnungsdatum',
        'abschlussdatum',
        'schutzfrist',
        'Ablage_Pr\xe4fix',
        'Ablage_Nr',
        'Beschreibung',
    ]

    def __init__(self, dossiers):
        self.dossiers = dossiers

    def __call__(self):
        lines = []
        for dossier in self.dossiers:
            binding = dossier.binding()
            data = {
                'dossier_id': binding.id,
                'Mandant': get_current_admin_unit().label(),
                'Ordnungsystem_Version': dossier.parents()[0].version,
                'Ordnungssystem_Pfad': self.repository_path(dossier),
                'Dossier_Titel': dossier.obj.title,
                'entstehungszeitraum_von': format_date(
                    binding.entstehungszeitraum.von.datum),
                'entstehungszeitraum_bis': format_date(
                    binding.entstehungszeitraum.bis.datum),
                'klassifizierungskategorie': binding.klassifizierungskategorie,
                'datenschutz': binding.datenschutz,
                'oeffentlichkeitsstatus': binding.oeffentlichkeitsstatus,
                'aktenzeichen': binding.aktenzeichen,
                'eroeffnungsdatum': format_date(dossier.binding().eroeffnungsdatum.datum),
                'abschlussdatum': format_date(dossier.binding().abschlussdatum.datum),
                'schutzfrist': binding.schutzfrist,
                'Ablage_Pr\xe4fix': dossier.obj.filing_prefix,
                'Ablage_Nr': self.filing_number(dossier),
                'Beschreibung': dossier.obj.description,
            }

            for key, value in data.items():
                if isinstance(value, unicode):
                    data[key] = value.encode('utf-8')

            lines.append(data)

        return lines

    def repository_path(self, dossier):
        # skip dossier itself
        return u'/'.join(
            [parent.Title().decode('utf-8') for parent in dossier.parents()[:-1]])

    def filing_number(self, dossier):
        if IFilingNumberMarker.providedBy(dossier.obj):
            return IFilingNumber(dossier.obj).filing_no


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
                    data = {
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
                    }

                    for key, value in data.items():
                        if isinstance(value, unicode):
                            data[key] = value.encode('utf-8')

                    lines.append(data)

        return lines


class DispositionDossierPerTypeCSVReporter(object):

    def __init__(self, dossiers):
        self.dossiers = dossiers

    def __call__(self):
        values_per_type = {}
        for dossier in self.dossiers:
            dossier_type = IDossier(dossier.obj).dossier_type
            if not dossier_type:
                continue

            if not dossier.binding().zusatzDaten:
                continue

            value = {'dossier_id': dossier.binding().id}
            value.update(
                {item.name: item.value()
                 for item in dossier.binding().zusatzDaten.merkmal})

            if dossier_type not in values_per_type:
                values_per_type[dossier_type] = []

            values_per_type[dossier_type].append(value)

        return values_per_type
