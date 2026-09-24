class DomainError(Exception):
    """Base class for business rule violations. Carries a user-facing message."""

    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = 404


class PermissionDeniedError(DomainError):
    status_code = 403


class ConflictError(DomainError):
    status_code = 409


class ValidationError(DomainError):
    status_code = 422


class AuthenticationError(DomainError):
    status_code = 401
