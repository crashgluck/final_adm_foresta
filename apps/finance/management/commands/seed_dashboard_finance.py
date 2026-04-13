import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.finance.models import FinancialMovement, FinancialMovementCategory, FinancialMovementType, PaymentMethod
from apps.parcels.models import Parcel


class Command(BaseCommand):
    help = 'Genera movimientos financieros realistas para alimentar dashboard y analítica.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=120, help='Cantidad de días hacia atrás a generar')
        parser.add_argument('--truncate', action='store_true', help='Eliminar movimientos financieros existentes antes de generar')
        parser.add_argument('--seed', type=int, default=42, help='Semilla para reproducibilidad')

    def handle(self, *args, **options):
        random.seed(options['seed'])

        if options['truncate']:
            deleted = FinancialMovement.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Se eliminaron {deleted} movimientos existentes.'))

        parcels = list(Parcel.objects.filter(is_deleted=False).values_list('id', flat=True))
        if not parcels:
            self.stdout.write(self.style.ERROR('No hay parcelas disponibles para generar datos.'))
            return

        days = max(1, options['days'])
        today = timezone.localdate()

        payment_categories = [
            FinancialMovementCategory.PAYMENT_GC,
            FinancialMovementCategory.PAYMENT_SERVICE,
            FinancialMovementCategory.PAYMENT_AGREEMENT,
            FinancialMovementCategory.PAYMENT_FINE,
        ]
        expense_categories = [
            FinancialMovementCategory.OPERATIONAL_EXPENSE,
            FinancialMovementCategory.MAINTENANCE_EXPENSE,
            FinancialMovementCategory.SECURITY_EXPENSE,
            FinancialMovementCategory.OTHER_EXPENSE,
        ]
        methods = [
            PaymentMethod.TRANSFER,
            PaymentMethod.CASH,
            PaymentMethod.CARD,
            PaymentMethod.ONLINE,
        ]

        created = 0
        for offset in range(days):
            current_day = today - timedelta(days=offset)
            weekday = current_day.weekday()

            income_count = random.randint(8, 20) if weekday < 5 else random.randint(3, 10)
            expense_count = random.randint(1, 5)

            for _ in range(income_count):
                parcel_id = random.choice(parcels)
                category = random.choices(payment_categories + [FinancialMovementCategory.OTHER_INCOME], weights=[40, 30, 15, 10, 5], k=1)[0]
                base_amount = random.randint(30000, 180000)
                if category == FinancialMovementCategory.PAYMENT_AGREEMENT:
                    base_amount = random.randint(90000, 280000)
                elif category == FinancialMovementCategory.PAYMENT_FINE:
                    base_amount = random.randint(20000, 120000)

                occurred = datetime.combine(current_day, time(hour=random.randint(8, 21), minute=random.randint(0, 59)))
                occurred = timezone.make_aware(occurred, timezone.get_current_timezone())

                FinancialMovement.objects.create(
                    parcela_id=parcel_id,
                    movement_type=FinancialMovementType.INCOME,
                    category=category,
                    amount=Decimal(base_amount),
                    occurred_at=occurred,
                    payment_method=random.choice(methods),
                    is_confirmed=True,
                    source_label='seed_dashboard',
                    description='Movimiento de ingreso generado para analítica',
                    reference=f'ING-{current_day:%Y%m%d}-{random.randint(1000, 9999)}',
                )
                created += 1

            for _ in range(expense_count):
                category = random.choice(expense_categories)
                base_amount = random.randint(20000, 140000)
                if category == FinancialMovementCategory.SECURITY_EXPENSE:
                    base_amount = random.randint(70000, 220000)

                occurred = datetime.combine(current_day, time(hour=random.randint(7, 20), minute=random.randint(0, 59)))
                occurred = timezone.make_aware(occurred, timezone.get_current_timezone())

                FinancialMovement.objects.create(
                    parcela_id=random.choice(parcels) if random.random() < 0.7 else None,
                    movement_type=FinancialMovementType.EXPENSE,
                    category=category,
                    amount=Decimal(base_amount),
                    occurred_at=occurred,
                    payment_method=PaymentMethod.OTHER,
                    is_confirmed=True,
                    source_label='seed_dashboard',
                    description='Movimiento de egreso generado para analítica',
                    reference=f'EGR-{current_day:%Y%m%d}-{random.randint(1000, 9999)}',
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Se generaron {created} movimientos financieros para dashboard.'))
