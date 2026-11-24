from __future__ import annotations

_TO_WESTERN = {
    **{0x0660 + i: str(i) for i in range(10)},
    **{0x06F0 + i: str(i) for i in range(10)},
}
_TO_ARABIC = {ord(str(i)): chr(0x0660 + i) for i in range(10)}


def to_western_digits(text: str) -> str:
    """Convert Arabic-Indic (٠-٩) and Persian (۰-۹) digits to 0-9. Everything else is left untouched."""
    return text.translate(_TO_WESTERN)


def to_arabic_digits(text: str) -> str:
    """Convert 0-9 to Arabic-Indic digits (٠-٩)."""
    return text.translate(_TO_ARABIC)
