from __future__ import annotations

import re
from typing import NamedTuple


class ParcelCodeParts(NamedTuple):
    code: str
    letter: str
    number: int
    suffix: str


PARCEL_CODE_PATTERN = re.compile(r'^([A-Z]{1,3})[-\s]*0*([0-9]{1,4})([A-Z]{0,2})$')


def normalize_email(value: str | None) -> str:
    if not value:
        return ''
    return value.strip().lower()


def normalize_phone(value: str | None) -> str:
    if not value:
        return ''
    cleaned = re.sub(r'[^0-9+]', '', str(value))
    return cleaned[:25]


def normalize_rut_number(value: str | None) -> str:
    if not value:
        return ''
    return re.sub(r'[^0-9]', '', str(value))


def normalize_rut_dv(value: str | None) -> str:
    if not value:
        return ''
    return str(value).strip().upper()


def parse_parcel_code(raw: str | None) -> ParcelCodeParts | None:
    if not raw:
        return None
    value = str(raw).upper().strip()
    value = re.sub(r'\s+', '', value)
    value = value.replace('_', '-')
    if '-' not in value and re.match(r'^[A-Z]{1,3}[0-9]', value):
        value = re.sub(r'^([A-Z]{1,3})([0-9].*)$', r'\1-\2', value)
    match = PARCEL_CODE_PATTERN.match(value)
    if not match:
        return None

    letter = match.group(1)
    number = int(match.group(2))
    suffix = match.group(3) or ''
    canonical = f'{letter}-{number}{suffix}'
    return ParcelCodeParts(code=canonical, letter=letter, number=number, suffix=suffix)


def normalize_parcel_code(raw: str | None) -> str:
    parsed = parse_parcel_code(raw)
    return parsed.code if parsed else ''

