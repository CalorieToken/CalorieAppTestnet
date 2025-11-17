import re
from decimal import ROUND_DOWN, Decimal

# XRPL validators and parsers used across screens

HEX40_RE = re.compile(r"^[0-9A-Fa-f]{40}$")
ALNUM_CODE_RE = re.compile(r"^[A-Za-z0-9]{3,12}$")


def is_address_format(address: str) -> bool:
    if not address or len(address) < 25:
        return False
    return address.startswith("r")


def is_valid_currency_code(code: str) -> bool:
    if not code:
        return False
    return bool(HEX40_RE.fullmatch(code)) or bool(ALNUM_CODE_RE.fullmatch(code))


def parse_issued_amount(text: str) -> str:
    """
    Parse a text amount for issued currencies and clamp to XRPL precision.
    Returns a string suitable for IssuedCurrencyAmount.value.
    Raises ValueError on invalid input.
    """
    amt = Decimal(text)
    if amt <= 0:
        raise ValueError("Amount must be positive")
    quant = Decimal("1e-16")
    amt = amt.quantize(quant, rounding=ROUND_DOWN).normalize()
    # Ensure plain string (avoid scientific notation for small values)
    return format(amt, "f")


def parse_taxon(text: str) -> int:
    value = int(text)
    if value < 0:
        raise ValueError("Taxon must be non-negative")
    return value
