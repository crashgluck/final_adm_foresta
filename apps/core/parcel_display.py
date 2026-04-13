from __future__ import annotations

from apps.people.models import OwnershipType


def get_parcel_owner_display(parcel) -> tuple[str, str]:
    if not parcel:
        return '', ''

    parcel_code = parcel.codigo_parcela

    ownerships_attr = getattr(parcel, 'ownerships', None)
    ownerships = ownerships_attr.all() if ownerships_attr is not None else []
    principal = next(
        (
            ownership
            for ownership in ownerships
            if not ownership.is_deleted and ownership.is_active and ownership.tipo == OwnershipType.PRINCIPAL and ownership.persona
        ),
        None,
    )

    if not principal:
        return parcel_code, parcel_code

    owner_name = principal.persona.nombre_completo
    display = f'{parcel_code} - {owner_name}'.strip(' -')
    return parcel_code, display

