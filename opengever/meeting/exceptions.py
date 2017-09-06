class AgendaItemListAlreadyGenerated(Exception):
    """An agenda item list could not be generated as there already is one."""


class AgendaItemListMissingTemplate(Exception):
    """An agenda item list could not be generated as is no template defined."""


class NoSubmittedDocument(Exception):
    """A document could not be updates remotely since it is not a submitted
    document.
    """


class ProtocolAlreadyGenerated(Exception):
    """The protocol could not be generated since another protocl is already
    present.
    """


class WordMeetingImplementationDisabledError(Exception):
    """The word meeting implementation feature is not enabled but a method
    was called which requires this feature.
    """


class MissingMeetingDossierPermissions(Exception):
    """The user has access to a meeting but no access to the meeting's dossier.
    """


class MissingAdHocTemplate(Exception):
    """No ad-hoc template could be found for the committee or its container.
    """
