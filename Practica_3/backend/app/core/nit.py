import re


LEGACY_NIT_PATTERN = re.compile(
    r"^[0-9]{1,8}-[0-9K]$"
)

CURRENT_NIT_PATTERN = re.compile(
    r"^[0-9]{9}$"
)


def normalize_nit(value: str) -> str:
    normalized = (
        value.strip()
        .upper()
        .replace(" ", "")
    )

    if normalized == "C/F":
        return "CF"

    return normalized


def validate_nit_format(value: str) -> bool:
    normalized = normalize_nit(value)

    return bool(
        normalized == "CF"
        or CURRENT_NIT_PATTERN.fullmatch(normalized)
        or LEGACY_NIT_PATTERN.fullmatch(normalized)
    )


def classify_nit(value: str) -> str:
    normalized = normalize_nit(value)

    if normalized == "CF":
        return "CONSUMIDOR_FINAL"

    if CURRENT_NIT_PATTERN.fullmatch(normalized):
        return "NIT_NUMERICO"

    if LEGACY_NIT_PATTERN.fullmatch(normalized):
        return "NIT_LEGADO"

    return "INVALIDO"
