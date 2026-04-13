from django.core.management.base import BaseCommand

from apps.accounts.models import User, UserRole


class Command(BaseCommand):
    help = 'Crea un usuario administrador inicial si no existe.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--first-name', default='Admin')
        parser.add_argument('--last-name', default='System')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Usuario {email} ya existe'))
            return

        user = User.objects.create_user(
            email=email,
            password=options['password'],
            first_name=options['first_name'],
            last_name=options['last_name'],
            role=UserRole.ADMINISTRADOR,
            is_staff=True,
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Usuario admin creado: {user.email}'))

