from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.data_imports.services.legacy_system_importer import DEFAULT_MODULES, LegacySystemImporter


class Command(BaseCommand):
    help = 'Importa datos desde el sistema legacy (SQLite) hacia el backend actual.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--legacy-db',
            default=r'C:\Users\crisv\Programacion\mantis-react\mantis-free-react-admin-template\backend\db.sqlite3',
            help='Ruta al SQLite del sistema antiguo',
        )
        parser.add_argument('--dry-run', action='store_true', help='Ejecuta en modo simulación')
        parser.add_argument(
            '--modules',
            default='',
            help=f'Lista separada por coma. Disponibles: {", ".join(DEFAULT_MODULES)}',
        )
        parser.add_argument('--user-email', default='', help='Email del usuario que ejecuta la importación')

    def handle(self, *args, **options):
        user = None
        if options['user_email']:
            user = User.objects.filter(email__iexact=options['user_email']).first()

        modules = [item.strip() for item in options['modules'].split(',') if item.strip()] if options['modules'] else None
        importer = LegacySystemImporter(
            legacy_db_path=options['legacy_db'],
            dry_run=options['dry_run'],
            initiated_by=user,
            modules=modules,
        )
        job = importer.run()
        self.stdout.write(self.style.SUCCESS(f'Legacy import job {job.id} finalizado con estado {job.status}'))
        self.stdout.write(
            f'inserted={job.total_inserted}, updated={job.total_updated}, skipped={job.total_skipped}, '
            f'errors={job.total_errors}, warnings={job.total_warnings}'
        )

