def decode_currency_code(code: str) -> str:
    """
    Decode a 40-hex XRPL currency code to ASCII if possible.
    If not hex or not decodable/printable, return the original code.
    """
    try:
        if isinstance(code, str) and len(code) == 40:
            decoded = bytes.fromhex(code).decode("utf-8").rstrip("\x00")
            if decoded and decoded.isprintable():
                return decoded
    except Exception:
        pass
    return code
