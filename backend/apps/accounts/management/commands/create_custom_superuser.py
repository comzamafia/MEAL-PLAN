"""
Create custom superuser for production.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create custom superuser for production'

    def handle(self, *args, **options):
        email = 'mrdamrongsakn@gmail.com'
        password = '48rH2%36#'

        # Delete existing user with this email to avoid conflicts
        User.objects.filter(email=email).delete()

        # Create superuser
        user = User.objects.create_superuser(
            email=email,
            username='mrdamrongsakn',
            password=password,
            first_name='Admin',
            last_name='User',
        )

        self.stdout.write(self.style.SUCCESS(f'Created superuser: {user.email}'))
