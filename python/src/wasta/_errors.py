from __future__ import annotations


class WastaError(ValueError):
    """Base class for every error raised by wasta. ``code`` is stable and safe to branch on."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class InvalidPhoneError(WastaError):
    pass


class InvalidNationalIdError(WastaError):
    pass


class TafqeetError(WastaError):
    pass


# Show errors as wasta.InvalidPhoneError rather than wasta._errors.InvalidPhoneError.
for _error in (WastaError, InvalidPhoneError, InvalidNationalIdError, TafqeetError):
    _error.__module__ = "wasta"
