from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.access_control.models import AccessRecord, AccessSource, AccessStatus, BlacklistEntry
from apps.accounts.models import User, UserRole
from apps.acquisitions.models import AcquisitionStatus, RFIDCard, RemoteControl, VehicleLogo
from apps.core.normalizers import normalize_parcel_code, normalize_rut_dv, normalize_rut_number, parse_parcel_code
from apps.core.validators import validate_rut
from apps.data_imports.models import ImportJob, ImportStatus
from apps.maps_app.models import Objective, ObjectiveStatus, ParcelMapGeometry, Visit
from apps.missions.models import DroneFlight, Mission, MissionMediaType, MissionReport, MissionStatus
from apps.parcels.models import Parcel, ParcelStatus
from apps.people.models import OwnershipType, ParcelOwnership, Person
from apps.supervisor.models import NotificationFine, NotificationStatus, Round, RoundStatus, Shift, ShiftStatus

DEFAULT_MODULES = [
    'users',
    'owners',
    'blacklist',
    'access',
    'objectives',
    'visits',
    'missions',
    'drone_flights',
    'mission_reports',
    'acquisitions',
    'supervisor',
]


@dataclass
class ImportCounter:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    warnings: int = 0

    def as_dict(self):
        return {
            'inserted': self.inserted,
            'updated': self.updated,
            'skipped': self.skipped,
            'errors': self.errors,
            'warnings': self.warnings,
        }


@dataclass
class LegacyImportContext:
    users: dict[int, User] = field(default_factory=dict)
    owners: dict[int, tuple[Parcel | None, Person | None]] = field(default_factory=dict)
    objectives: dict[int, Objective] = field(default_factory=dict)
    missions: dict[int, Mission] = field(default_factory=dict)
    shifts: dict[int, Shift] = field(default_factory=dict)


def _clean_alnum_upper(value) -> str:
    return ''.join(ch for ch in str(value or '').upper() if ch.isalnum())


def _parse_datetime(value):
    if value in (None, ''):
        return None
    if isinstance(value, datetime):
        return timezone.make_aware(value) if timezone.is_naive(value) else value
    raw = str(value).strip().replace(' ', 'T')
    raw = raw.replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(raw)
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
    except ValueError:
        return None


def _parse_date(value):
    if value in (None, ''):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    raw = str(value).strip()
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _safe_decimal(value, default=Decimal('0')):
    if value in (None, ''):
        return default
    try:
        return Decimal(str(value))
    except Exception:
        return default


def _role_from_legacy(value: str) -> str:
    mapping = {
        'superuser': UserRole.SUPERADMIN,
        'admin': UserRole.ADMINISTRADOR,
        'supervisor': UserRole.OPERADOR,
        'operator': UserRole.OPERADOR,
        'viewer': UserRole.CONSULTA,
    }
    return mapping.get((value or '').strip().lower(), UserRole.OPERADOR)


def _canonical_parcel_code(lot, parcel, fallback_id: int) -> str:
    raw_code = f'{lot or ""}-{parcel or ""}'.strip('-')
    normalized = normalize_parcel_code(raw_code)
    if normalized:
        return normalized

    lot_letters = ''.join(ch for ch in str(lot or '').upper() if ch.isalpha())[:3] or 'L'
    parcel_token = ''.join(ch for ch in str(parcel or '').upper() if ch.isalnum())
    match = re.match(r'^0*([0-9]{1,4})([A-Z]{0,2})$', parcel_token)
    if match:
        number = int(match.group(1))
        suffix = match.group(2) or ''
        recovered = f'{lot_letters}-{number}{suffix}'
        if parse_parcel_code(recovered):
            return recovered
    return f'L-{fallback_id}'


def _parse_coordinates(raw_value):
    if not raw_value:
        return None
    if isinstance(raw_value, (list, dict)):
        return raw_value
    try:
        data = json.loads(raw_value)
    except Exception:
        return None
    return data if isinstance(data, (list, dict)) else None


class LegacySystemImporter:
    def __init__(self, legacy_db_path: str, dry_run: bool = False, initiated_by: User | None = None, modules: list[str] | None = None):
        self.legacy_db_path = Path(legacy_db_path)
        self.dry_run = dry_run
        self.initiated_by = initiated_by
        self.modules = modules or DEFAULT_MODULES
        self.context = LegacyImportContext()
        self.owner_row_errors: list[dict] = []

    def run(self) -> ImportJob:
        if not self.legacy_db_path.exists():
            raise FileNotFoundError(f'Base legacy no encontrada: {self.legacy_db_path}')

        job = ImportJob.objects.create(
            source_file=self.legacy_db_path.name,
            source_hash=self._hash_file(),
            source_path=str(self.legacy_db_path),
            dry_run=self.dry_run,
            status=ImportStatus.RUNNING,
            initiated_by=self.initiated_by,
            details={'type': 'legacy_sqlite', 'modules': self.modules, 'results': {}},
        )

        module_handlers = [
            ('users', self._import_users),
            ('owners', self._import_owners),
            ('blacklist', self._import_blacklist),
            ('access', self._import_access_records),
            ('objectives', self._import_objectives),
            ('visits', self._import_visits),
            ('missions', self._import_missions),
            ('drone_flights', self._import_drone_flights),
            ('mission_reports', self._import_mission_reports),
            ('acquisitions', self._import_acquisitions),
            ('supervisor', self._import_supervisor),
        ]

        totals = ImportCounter()
        conn = sqlite3.connect(str(self.legacy_db_path))
        conn.row_factory = sqlite3.Row
        try:
            for module_name, handler in module_handlers:
                if module_name not in self.modules:
                    continue
                counter = ImportCounter()
                try:
                    handler(conn, counter)
                except Exception:
                    counter.errors += 1
                totals.inserted += counter.inserted
                totals.updated += counter.updated
                totals.skipped += counter.skipped
                totals.errors += counter.errors
                totals.warnings += counter.warnings
                job.details['results'][module_name] = counter.as_dict()
                if module_name == 'owners' and self.owner_row_errors:
                    job.details['owners_row_errors'] = self.owner_row_errors
                job.save(update_fields=['details'])
        finally:
            conn.close()

        job.total_inserted = totals.inserted
        job.total_updated = totals.updated
        job.total_skipped = totals.skipped
        job.total_errors = totals.errors
        job.total_warnings = totals.warnings
        job.finished_at = timezone.now()
        if totals.errors == 0:
            job.status = ImportStatus.SUCCESS
        elif totals.inserted or totals.updated:
            job.status = ImportStatus.PARTIAL
        else:
            job.status = ImportStatus.FAILED
        job.save(
            update_fields=[
                'total_inserted',
                'total_updated',
                'total_skipped',
                'total_errors',
                'total_warnings',
                'finished_at',
                'status',
                'details',
            ]
        )
        return job

    def _hash_file(self) -> str:
        digest = hashlib.sha256()
        with self.legacy_db_path.open('rb') as fh:
            for chunk in iter(lambda: fh.read(4096), b''):
                digest.update(chunk)
        return digest.hexdigest()

    def _import_users(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute(
            'SELECT id, username, email, first_name, last_name, role, is_active, is_superuser, is_staff FROM accounts_user'
        ).fetchall()

        for row in rows:
            username = (row['username'] or '').strip() or f'legacy_user_{row["id"]}'
            email = (row['email'] or '').strip().lower() or f'{username}@legacy.local'
            defaults = {
                'username': username,
                'first_name': row['first_name'] or '',
                'last_name': row['last_name'] or '',
                'role': UserRole.SUPERADMIN if row['is_superuser'] else _role_from_legacy(row['role']),
                'is_active': bool(row['is_active']),
                'is_staff': bool(row['is_staff']) or bool(row['is_superuser']),
            }

            user, created = User.objects.get_or_create(email=email, defaults=defaults)
            if created:
                user.set_unusable_password()
                if not self.dry_run:
                    user.save()
                counter.inserted += 1
            else:
                changed = False
                for field, value in defaults.items():
                    if getattr(user, field) != value:
                        setattr(user, field, value)
                        changed = True
                if changed and not self.dry_run:
                    user.save(update_fields=['username', 'first_name', 'last_name', 'role', 'is_active', 'is_staff'])
                    counter.updated += 1
                else:
                    counter.skipped += 1
            self.context.users[row['id']] = user

    def _build_person_data(self, row):
        first_name = (row['first_name'] or '').strip()
        last_name = (row['last_name'] or '').strip()
        full_name = f'{first_name} {last_name}'.strip() or f'Legacy {row["id"]}'

        rut_raw = (row['rut'] or '').strip()
        dv_raw = (row['check_digit'] or '').strip()
        if '-' in rut_raw and not dv_raw:
            parts = rut_raw.split('-', maxsplit=1)
            rut_raw = parts[0]
            dv_raw = parts[1]
        rut_number = normalize_rut_number(rut_raw)
        rut_dv = normalize_rut_dv(dv_raw)
        if len(rut_number) > 12:
            rut_number = ''
            rut_raw = ''
            rut_dv = ''
        if rut_number and rut_dv and not validate_rut(rut_number, rut_dv):
            rut_number = ''
            rut_dv = ''

        return {
            'nombres': first_name[:120],
            'apellidos': last_name[:120],
            'nombre_completo': full_name[:255],
            'rut': rut_raw[:20],
            'rut_dv': rut_dv[:2],
            'email': (row['email'] or '').strip().lower(),
            'telefono_principal': (row['phone'] or row['secondary_phone_1'] or '').strip(),
            'telefono_secundario': (row['secondary_phone_2'] or '').strip(),
            'direccion_contacto': (row['address'] or '').strip()[:255],
            'activo': bool(row['is_active']),
            'notas': ((row['notes'] or '')[:1800]),
            'rut_normalizado': rut_number,
        }

    def _upsert_person(self, payload: dict, counter: ImportCounter) -> Person | None:
        rut_normalizado = payload.get('rut_normalizado') or ''
        person = None
        if rut_normalizado:
            person = Person.objects.filter(rut_normalizado=rut_normalizado, is_deleted=False).first()
        if not person:
            person = Person.objects.filter(
                nombre_completo__iexact=payload['nombre_completo'],
                email__iexact=payload['email'],
                is_deleted=False,
            ).first()

        defaults = payload.copy()
        defaults.pop('rut_normalizado', None)

        if person:
            changed = False
            for key, value in defaults.items():
                if value and getattr(person, key) != value:
                    setattr(person, key, value)
                    changed = True
            if changed and not self.dry_run:
                try:
                    person.save()
                    counter.updated += 1
                except ValidationError:
                    person.rut = ''
                    person.rut_dv = ''
                    person.email = ''
                    try:
                        person.save()
                        counter.warnings += 1
                    except ValidationError:
                        counter.errors += 1
                        return None
            else:
                counter.skipped += 1
            return person

        if self.dry_run:
            counter.inserted += 1
            return None
        try:
            person = Person.objects.create(**defaults)
            counter.inserted += 1
            return person
        except ValidationError:
            defaults['rut'] = ''
            defaults['rut_dv'] = ''
            defaults['email'] = ''
            try:
                person = Person.objects.create(**defaults)
                counter.inserted += 1
                counter.warnings += 1
                return person
            except ValidationError:
                try:
                    person = Person.objects.create(
                        nombre_completo=defaults['nombre_completo'],
                        nombres=defaults.get('nombres', ''),
                        apellidos=defaults.get('apellidos', ''),
                        activo=defaults.get('activo', True),
                    )
                    counter.inserted += 1
                    counter.warnings += 1
                    return person
                except ValidationError:
                    counter.errors += 1
                    return None

    def _import_owners(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute(
            '''
            SELECT id, first_name, last_name, rut, check_digit, lot, parcel, email, secondary_email, phone,
                   secondary_phone_1, secondary_phone_2, address, notes, is_active, map_coordinates, map_color
            FROM owners_usuarionuevo
            ORDER BY id
            '''
        ).fetchall()

        for row in rows:
            try:
                code = _canonical_parcel_code(row['lot'], row['parcel'], row['id'])
                parcel, parcel_created = Parcel.objects.get_or_create(
                    codigo_parcela_key=code,
                    defaults={
                        'codigo_parcela': code,
                        'estado': ParcelStatus.ACTIVA if row['is_active'] else ParcelStatus.INACTIVA,
                        'referencia_direccion': (row['address'] or '')[:255],
                    },
                )
                if parcel_created:
                    counter.inserted += 1
                else:
                    changed = False
                    if row['address'] and parcel.referencia_direccion != row['address']:
                        parcel.referencia_direccion = row['address'][:255]
                        changed = True
                    if changed and not self.dry_run:
                        parcel.save(update_fields=['referencia_direccion', 'updated_at'])
                        counter.updated += 1

                person_payload = self._build_person_data(row)
                person = self._upsert_person(person_payload, counter)
                self.context.owners[row['id']] = (parcel, person)

                if person and parcel:
                    active_primary = ParcelOwnership.objects.filter(
                        parcela=parcel,
                        tipo=OwnershipType.PRINCIPAL,
                        is_active=True,
                        is_deleted=False,
                    ).first()
                    if active_primary and active_primary.persona_id == person.id:
                        counter.skipped += 1
                    elif active_primary and active_primary.persona_id != person.id:
                        if not ParcelOwnership.objects.filter(
                            parcela=parcel, persona=person, tipo=OwnershipType.COPROPIETARIO, is_active=True, is_deleted=False
                        ).exists():
                            if not self.dry_run:
                                ParcelOwnership.objects.create(parcela=parcel, persona=person, tipo=OwnershipType.COPROPIETARIO)
                            counter.inserted += 1
                        else:
                            counter.skipped += 1
                    else:
                        if not self.dry_run:
                            ParcelOwnership.objects.create(parcela=parcel, persona=person, tipo=OwnershipType.PRINCIPAL)
                        counter.inserted += 1

                coordinates = _parse_coordinates(row['map_coordinates'])
                if coordinates:
                    defaults = {
                        'coordinates': coordinates,
                        'color': (row['map_color'] or '#51ff00')[:9],
                        'source_label': 'legacy.sqlite',
                    }
                    if not self.dry_run:
                        ParcelMapGeometry.objects.update_or_create(parcela=parcel, defaults=defaults)
            except Exception as exc:
                if len(self.owner_row_errors) < 200:
                    self.owner_row_errors.append({'legacy_owner_id': row['id'], 'message': str(exc)})
                counter.errors += 1

    def _import_blacklist(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute('SELECT rut, plate, reason, is_active FROM access_control_blacklistentry').fetchall()
        for row in rows:
            rut = (row['rut'] or '').strip().upper()
            plate = _clean_alnum_upper(row['plate'])
            reason = (row['reason'] or '').strip()[:255]
            is_active = bool(row['is_active'])
            existing = BlacklistEntry.objects.filter(rut=rut, plate=plate, is_deleted=False).first()
            if existing:
                changed = existing.reason != reason or existing.is_active != is_active
                if changed and not self.dry_run:
                    existing.reason = reason
                    existing.is_active = is_active
                    existing.save(update_fields=['reason', 'is_active', 'updated_at'])
                    counter.updated += 1
                else:
                    counter.skipped += 1
                continue
            if not self.dry_run:
                BlacklistEntry.objects.create(rut=rut, plate=plate, reason=reason, is_active=is_active)
            counter.inserted += 1

    def _owner_refs(self, legacy_owner_id: int):
        return self.context.owners.get(legacy_owner_id, (None, None))

    def _import_access_records(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute(
            '''
            SELECT id, owner_id, full_name, rut, plate, motive, company_name, access_datetime, note,
                   card_number, card_color, status, source
            FROM access_control_accessrecord
            ORDER BY id
            '''
        ).fetchall()
        for row in rows:
            parcela, person = self._owner_refs(row['owner_id'])
            access_datetime = _parse_datetime(row['access_datetime'])
            if not access_datetime:
                counter.warnings += 1
                continue

            lookup = {
                'parcela': parcela,
                'full_name': (row['full_name'] or '').strip()[:180],
                'rut': (row['rut'] or '').strip().upper(),
                'plate': _clean_alnum_upper(row['plate']),
                'access_datetime': access_datetime,
                'is_deleted': False,
            }
            existing = AccessRecord.objects.filter(**lookup).first()
            defaults = {
                'persona': person,
                'motive': (row['motive'] or '')[:200],
                'company_name': (row['company_name'] or '')[:150],
                'note': row['note'] or '',
                'card_number': (row['card_number'] or '')[:30],
                'card_color': (row['card_color'] or '')[:30],
                'status': (row['status'] or AccessStatus.ALLOWED)[:20],
                'source': (row['source'] or AccessSource.LEGACY_IMPORT)[:20],
                'created_from': f'legacy_access:{row["id"]}',
            }

            if existing:
                changed = False
                for field, value in defaults.items():
                    if getattr(existing, field) != value:
                        setattr(existing, field, value)
                        changed = True
                if changed and not self.dry_run:
                    existing.save()
                    counter.updated += 1
                else:
                    counter.skipped += 1
                continue

            if not self.dry_run:
                AccessRecord.objects.create(**lookup, **defaults)
            counter.inserted += 1

    def _import_objectives(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute(
            '''
            SELECT id, owner_id, assigned_to_id, title, description, latitude, longitude, coordinates, color, due_date, status
            FROM maps_app_objective
            ORDER BY id
            '''
        ).fetchall()
        for row in rows:
            parcela, person = self._owner_refs(row['owner_id'])
            defaults = {
                'parcela': parcela,
                'persona': person,
                'assigned_to': self.context.users.get(row['assigned_to_id']),
                'description': row['description'] or '',
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'coordinates': _parse_coordinates(row['coordinates']),
                'color': (row['color'] or '#51ff00')[:9],
                'due_date': _parse_date(row['due_date']),
                'status': (row['status'] or ObjectiveStatus.PENDING)[:20],
            }
            objective, created = Objective.objects.update_or_create(
                title=(row['title'] or f'Objetivo legacy #{row["id"]}')[:180],
                parcela=parcela,
                due_date=defaults['due_date'],
                defaults=defaults,
            )
            self.context.objectives[row['id']] = objective
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

    def _import_visits(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute(
            '''
            SELECT id, owner_id, objective_id, admitted_by_id, visitor_name, visitor_rut, vehicle_plate, purpose, visit_datetime, notes
            FROM maps_app_visit
            ORDER BY id
            '''
        ).fetchall()
        for row in rows:
            parcela, person = self._owner_refs(row['owner_id'])
            if not parcela:
                counter.warnings += 1
                continue
            visit_dt = _parse_datetime(row['visit_datetime'])
            if not visit_dt:
                counter.warnings += 1
                continue

            defaults = {
                'persona': person,
                'objective': self.context.objectives.get(row['objective_id']),
                'admitted_by': self.context.users.get(row['admitted_by_id']),
                'visitor_rut': (row['visitor_rut'] or '')[:20],
                'vehicle_plate': (row['vehicle_plate'] or '')[:20],
                'purpose': (row['purpose'] or '')[:200],
                'notes': row['notes'] or '',
            }
            _, created = Visit.objects.update_or_create(
                parcela=parcela,
                visitor_name=(row['visitor_name'] or '')[:150],
                visit_datetime=visit_dt,
                defaults=defaults,
            )
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

    def _import_missions(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute(
            '''
            SELECT id, owner_id, assigned_to_id, title, description, mission_type, team_name, status, scheduled_for, started_at, completed_at
            FROM missions_mission
            ORDER BY id
            '''
        ).fetchall()
        for row in rows:
            parcela, person = self._owner_refs(row['owner_id'])
            defaults = {
                'description': row['description'] or '',
                'mission_type': (row['mission_type'] or '')[:80],
                'parcela': parcela,
                'persona': person,
                'team_name': (row['team_name'] or '')[:120],
                'assigned_to': self.context.users.get(row['assigned_to_id']),
                'status': (row['status'] or MissionStatus.PLANNED)[:20],
                'scheduled_for': _parse_datetime(row['scheduled_for']),
                'started_at': _parse_datetime(row['started_at']),
                'completed_at': _parse_datetime(row['completed_at']),
            }
            mission, created = Mission.objects.update_or_create(title=(row['title'] or '')[:180], parcela=parcela, defaults=defaults)
            self.context.missions[row['id']] = mission
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

    def _import_drone_flights(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute(
            '''
            SELECT id, owner_id, pilot_id, flight_datetime, mission_code, team_code, battery_code,
                   takeoff_platform, notes, photo_path, video_path
            FROM missions_droneflight
            ORDER BY id
            '''
        ).fetchall()
        for row in rows:
            parcela, person = self._owner_refs(row['owner_id'])
            defaults = {
                'pilot': self.context.users.get(row['pilot_id']),
                'parcela': parcela,
                'persona': person,
                'flight_datetime': _parse_datetime(row['flight_datetime']) or timezone.now(),
                'mission_code': (row['mission_code'] or '')[:40],
                'team_code': (row['team_code'] or '')[:40],
                'battery_code': (row['battery_code'] or '')[:40],
                'takeoff_platform': (row['takeoff_platform'] or '')[:80],
                'notes': row['notes'] or '',
                'photo_path': (row['photo_path'] or '')[:255],
                'video_path': (row['video_path'] or '')[:255],
            }
            _, created = DroneFlight.objects.update_or_create(legacy_source_id=row['id'], defaults=defaults)
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

    def _import_mission_reports(self, conn: sqlite3.Connection, counter: ImportCounter):
        rows = conn.execute(
            '''
            SELECT id, mission_id, created_by_id, report_date, summary, media_url, media_type
            FROM missions_missionreport
            ORDER BY id
            '''
        ).fetchall()
        for row in rows:
            mission = self.context.missions.get(row['mission_id'])
            if not mission:
                counter.warnings += 1
                continue
            defaults = {
                'created_by': self.context.users.get(row['created_by_id']),
                'summary': row['summary'] or '',
                'media_url': row['media_url'] or '',
                'media_type': (row['media_type'] or MissionMediaType.NONE)[:20],
            }
            _, created = MissionReport.objects.update_or_create(
                mission=mission,
                report_date=_parse_date(row['report_date']) or timezone.localdate(),
                defaults=defaults,
            )
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

    def _import_acquisitions(self, conn: sqlite3.Connection, counter: ImportCounter):
        remote_rows = conn.execute(
            'SELECT owner_id, serial_number, model, status, issued_at FROM acquisitions_remotecontrol ORDER BY id'
        ).fetchall()
        for row in remote_rows:
            parcela, person = self._owner_refs(row['owner_id'])
            if not parcela:
                counter.warnings += 1
                continue
            defaults = {
                'parcela': parcela,
                'persona': person,
                'model': (row['model'] or '')[:100],
                'status': (row['status'] or AcquisitionStatus.ACTIVE)[:20],
                'issued_at': _parse_date(row['issued_at']),
            }
            _, created = RemoteControl.objects.update_or_create(serial_number=(row['serial_number'] or '')[:80], defaults=defaults)
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

        rfid_rows = conn.execute('SELECT owner_id, uid, color, status, issued_at FROM acquisitions_rfidcard ORDER BY id').fetchall()
        for row in rfid_rows:
            parcela, person = self._owner_refs(row['owner_id'])
            if not parcela:
                counter.warnings += 1
                continue
            defaults = {
                'parcela': parcela,
                'persona': person,
                'color': (row['color'] or '')[:40],
                'status': (row['status'] or AcquisitionStatus.ACTIVE)[:20],
                'issued_at': _parse_date(row['issued_at']),
            }
            _, created = RFIDCard.objects.update_or_create(uid=(row['uid'] or '')[:120], defaults=defaults)
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

        logo_rows = conn.execute(
            'SELECT owner_id, plate, logo_code, status, issued_at FROM acquisitions_vehiclelogo ORDER BY id'
        ).fetchall()
        for row in logo_rows:
            parcela, person = self._owner_refs(row['owner_id'])
            if not parcela:
                counter.warnings += 1
                continue
            defaults = {
                'parcela': parcela,
                'persona': person,
                'plate': (row['plate'] or '')[:20],
                'status': (row['status'] or AcquisitionStatus.ACTIVE)[:20],
                'issued_at': _parse_date(row['issued_at']),
            }
            _, created = VehicleLogo.objects.update_or_create(logo_code=(row['logo_code'] or '')[:120], defaults=defaults)
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

    def _import_supervisor(self, conn: sqlite3.Connection, counter: ImportCounter):
        shift_rows = conn.execute(
            'SELECT id, supervisor_id, name, start_datetime, end_datetime, status, notes FROM supervisor_shift ORDER BY id'
        ).fetchall()
        for row in shift_rows:
            defaults = {
                'supervisor': self.context.users.get(row['supervisor_id']),
                'start_datetime': _parse_datetime(row['start_datetime']) or timezone.now(),
                'end_datetime': _parse_datetime(row['end_datetime']),
                'status': (row['status'] or ShiftStatus.OPEN)[:20],
                'notes': row['notes'] or '',
            }
            shift, created = Shift.objects.update_or_create(name=(row['name'] or f'Turno #{row["id"]}')[:120], defaults=defaults)
            self.context.shifts[row['id']] = shift
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

        round_rows = conn.execute(
            'SELECT shift_id, guard_id, started_at, ended_at, status, notes FROM supervisor_round ORDER BY id'
        ).fetchall()
        for row in round_rows:
            shift = self.context.shifts.get(row['shift_id'])
            if not shift:
                counter.warnings += 1
                continue
            defaults = {
                'guard': self.context.users.get(row['guard_id']),
                'ended_at': _parse_datetime(row['ended_at']),
                'status': (row['status'] or RoundStatus.PLANNED)[:20],
                'notes': row['notes'] or '',
            }
            _, created = Round.objects.update_or_create(
                shift=shift,
                started_at=_parse_datetime(row['started_at']) or timezone.now(),
                defaults=defaults,
            )
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1

        notification_rows = conn.execute(
            '''
            SELECT owner_id, shift_id, title, description, amount, status, issued_at, due_date, paid_at
            FROM supervisor_notificationfine
            ORDER BY id
            '''
        ).fetchall()
        for row in notification_rows:
            parcela, person = self._owner_refs(row['owner_id'])
            defaults = {
                'persona': person,
                'shift': self.context.shifts.get(row['shift_id']),
                'description': row['description'] or '',
                'amount': _safe_decimal(row['amount']),
                'status': (row['status'] or NotificationStatus.PENDING)[:20],
                'due_date': _parse_date(row['due_date']),
                'paid_at': _parse_datetime(row['paid_at']),
            }
            _, created = NotificationFine.objects.update_or_create(
                parcela=parcela,
                title=(row['title'] or '')[:160],
                issued_at=_parse_datetime(row['issued_at']) or timezone.now(),
                defaults=defaults,
            )
            if created:
                counter.inserted += 1
            else:
                counter.updated += 1
