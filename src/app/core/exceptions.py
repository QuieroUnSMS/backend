class InvalidSessionError(Exception):
    """Raised when a session credential is missing or unknown."""


class IdentitySuspendedError(Exception):
    """Raised when an identity is suspended for acceptable use."""


class DuplicateIdentifierError(Exception):
    """Raised when email or phone already belongs to another identity."""


class AlreadyRegisteredError(Exception):
    """Raised when registration is attempted on an already registered identity."""


class RegistrationRequiredError(Exception):
    """Raised when a registered account is required for the operation."""