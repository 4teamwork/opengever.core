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


class MissingMeetingDossierPermissions(Exception):
    """The user has access to a meeting but no access to the meeting's dossier.
    """


class MissingAdHocTemplate(Exception):
    """No ad-hoc template could be found for the committee or its container.
    """


class MissingProtocolHeaderTemplate(Exception):
    """No protocol header template could be found for the committee or its container.
    """


class WrongAgendaItemState(Exception):
    """The agenda item is not in the correct state to perform the desired
    action.
    """


class CannotExecuteTransition(Exception):
    """The workflow transition cannot be executed."""


class SablonProcessingFailed(Exception):
    """Processing of the sablon template failed."""


class MultiplePeriodsFound(Exception):
    """Multiple periods were found for the same date."""


class ProposalMovedOutsideOfMainDossierError(Exception):
    """The proposal have been moved outside of its main dossier which is not allowed.
    """
