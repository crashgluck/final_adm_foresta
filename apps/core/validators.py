from __future__ import annotations


def validate_rut(number: str, dv: str) -> bool:
    number = ''.join(ch for ch in str(number or '') if ch.isdigit())
    dv = str(dv or '').strip().upper()
    if not number or not dv:
        return False

    reverse_digits = map(int, reversed(number))
    factors = [2, 3, 4, 5, 6, 7]
    acc = 0
    for idx, digit in enumerate(reverse_digits):
        acc += digit * factors[idx % len(factors)]

    remainder = 11 - (acc % 11)
    if remainder == 11:
        expected = '0'
    elif remainder == 10:
        expected = 'K'
    else:
        expected = str(remainder)

    return expected == dv

