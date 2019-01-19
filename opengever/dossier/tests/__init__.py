from datetime import datetime
from plone.app.testing import TEST_USER_ID


EXPECTED_USER_DOC_PROPERTIES = {
    'User.ID': 'kathi.barfuss',
    'User.FullName': u'B\xe4rfuss K\xe4thi',
    'ogg.user.userid': 'kathi.barfuss',
    'ogg.user.title': u'B\xe4rfuss K\xe4thi',
    'ogg.user.firstname': u'K\xe4thi',
    'ogg.user.lastname': u'B\xe4rfuss',
    'ogg.user.directorate': u'Staatsarchiv',
    'ogg.user.directorate_abbr': u'Arch',
    'ogg.user.department': u'Staatskanzlei',
    'ogg.user.department_abbr': u'SK',
    'ogg.user.email': u'foo@example.com',
    'ogg.user.email2': u'bar@example.com',
    'ogg.user.url': u'http://www.example.com',
    'ogg.user.phone_office': u'012 34 56 78',
    'ogg.user.phone_fax': u'012 34 56 77',
    'ogg.user.phone_mobile': u'012 34 56 76',
    'ogg.user.salutation': u'Prof. Dr.',
    'ogg.user.description': u'nix',
    'ogg.user.address1': u'Kappelenweg 13',
    'ogg.user.address2': u'Postfach 1234',
    'ogg.user.zip_code': u'1234',
    'ogg.user.city': u'Vorkappelen',
    'ogg.user.country': u'Schweiz',
}


OGDS_USER_ATTRIBUTES = {
    'firstname': u'Peter',
    'lastname': u'M\xfcller',
    'directorate': u'Staatsarchiv',
    'directorate_abbr': u'Arch',
    'department': u'Staatskanzlei',
    'department_abbr': u'SK',
    'email': u'foo@example.com',
    'email2': u'bar@example.com',
    'url': u'http://www.example.com',
    'phone_office': u'012 34 56 78',
    'phone_fax': u'012 34 56 77',
    'phone_mobile': u'012 34 56 76',
    'salutation': u'Prof. Dr.',
    'description': u'nix',
    'address1': u'Kappelenweg 13',
    'address2': u'Postfach 1234',
    'zip_code': u'1234',
    'city': u'Vorkappelen',
    'country': u'Schweiz',
}

EXPECTED_DOSSIER_PROPERTIES = {
    'Dossier.ReferenceNumber': 'Client1 1.1 / 1',
    'Dossier.Title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
    'ogg.dossier.title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
    'ogg.dossier.reference_number': 'Client1 1.1 / 1',
    'ogg.dossier.sequence_number': '1',
    'ogg.dossier.external_reference': u'qpr-900-9001-\xf7',
}


EXPECTED_DOCUMENT_PROPERTIES = {
    'Document.ReferenceNumber': 'Client1 1.1 / 1 / 12',
    'Document.SequenceNumber': '12',
    'ogg.document.title': u'Vertr\xe4gsentwurf',
    'ogg.document.reference_number': 'Client1 1.1 / 1 / 12',
    'ogg.document.sequence_number': '12',
    'ogg.document.document_author': TEST_USER_ID,
    'ogg.document.document_date': datetime(2010, 1, 3),
    'ogg.document.document_type': u'Contract',
    'ogg.document.reception_date': datetime(2010, 1, 3),
    'ogg.document.delivery_date': datetime(2010, 1, 3),
    'ogg.document.version_number': 0,
}

EXPECTED_TASKDOCUMENT_PROPERTIES = {
    'Document.ReferenceNumber': 'Client1 1.1 / 1 / 31',
    'Document.SequenceNumber': '31',
    'ogg.document.title': u'Feedback zum Vertragsentwurf',
    'ogg.document.reference_number': 'Client1 1.1 / 1 / 31',
    'ogg.document.document_date': datetime(2016, 8, 31, 0, 0),
    'ogg.document.sequence_number': '31',
    'ogg.document.version_number': 0
}

EXPECTED_PROPOSALDOCUMENT_PROPERTIES = {
    'Document.ReferenceNumber': 'Client1 1.1 / 1 / 16',
    'Document.SequenceNumber': '16',
    'ogg.document.title': u'Kommentar zum Vertragsentwurf',
    'ogg.document.reference_number': 'Client1 1.1 / 1 / 16',
    'ogg.document.document_date': datetime(2016, 8, 31, 0, 0),
    'ogg.document.sequence_number': '16',
    'ogg.document.version_number': 0
}

EXPECTED_MEETING_PROPERTIES = {
    'ogg.meeting.agenda_item_number': '',
    'ogg.meeting.agenda_item_number_raw': '',
    'ogg.meeting.decision_number': '',
    'ogg.meeting.proposal_state': 'Submitted',
    'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
    'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen'
}

EXPECTED_DOC_PROPERTIES = dict(
    EXPECTED_USER_DOC_PROPERTIES.items() +
    EXPECTED_DOSSIER_PROPERTIES.items() +
    EXPECTED_DOCUMENT_PROPERTIES.items()
)

EXPECTED_TASKDOC_PROPERTIES = dict(
    EXPECTED_USER_DOC_PROPERTIES.items() +
    EXPECTED_DOSSIER_PROPERTIES.items() +
    EXPECTED_TASKDOCUMENT_PROPERTIES.items()
)

EXPECTED_PROPOSALDOC_PROPERTIES = dict(
    EXPECTED_USER_DOC_PROPERTIES.items() +
    EXPECTED_DOSSIER_PROPERTIES.items() +
    EXPECTED_MEETING_PROPERTIES.items() +
    EXPECTED_PROPOSALDOCUMENT_PROPERTIES.items()
)
