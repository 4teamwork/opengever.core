from opengever.base.behaviors.changed import IChanged
from opengever.disposition.ech0160.bindings import arelda
from opengever.disposition.ech0160.model.additional_data import get_additional_data
from opengever.disposition.ech0160.utils import set_classification_attributes
from opengever.disposition.ech0160.utils import voc_term_title
from opengever.document.behaviors.metadata import IDocumentMetadata


class Document(object):
    """eCH-0160 dokumentGeverSIP"""

    def __init__(self, obj):
        self.obj = obj
        self.file_refs = []
        self.files = []

    def binding(self):
        dokument = arelda.dokumentGeverSIP(id=u'_{}'.format(self.obj.UID()))
        dokument.titel = self.obj.Title().decode('utf8')

        md = IDocumentMetadata(self.obj)
        if md.document_author:
            dokument.autor.append(md.document_author)

        if self.obj.digitally_available:
            dokument.erscheinungsform = u'digital'
        else:
            dokument.erscheinungsform = u'nicht digital'

        dokument.dokumenttyp = voc_term_title(
            IDocumentMetadata['document_type'], md.document_type)

        dokument.registrierdatum = arelda.historischerZeitpunkt(
            self.obj.created().asdatetime().date())

        dokument.entstehungszeitraum = arelda.historischerZeitraum()
        dokument.entstehungszeitraum.von = arelda.historischerZeitpunkt(
            self.obj.created().asdatetime().date())
        dokument.entstehungszeitraum.bis = arelda.historischerZeitpunkt(
            IChanged(self.obj).changed.date())

        set_classification_attributes(dokument, self.obj)

        additional_data = get_additional_data(self.obj)
        if additional_data:
            dokument.zusatzDaten = additional_data

        for file_ref in self.file_refs:
            dokument.dateiRef.append(file_ref)

        return dokument
