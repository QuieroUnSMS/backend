class ContactNotFoundError(Exception):
    """Raised when a contact id does not exist."""


class DuplicatePhoneError(Exception):
    """Raised when phone_e164 conflicts with another contact."""