class DuplicatePendingInvitation(Exception):
    """Tried to invite an e-mail address that already has a pending invitation.
    """


class MultipleUsersFound(Exception):
    """Found multiple users for the invitaion."""
