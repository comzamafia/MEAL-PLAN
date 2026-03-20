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

        self.stdout.write(f'Creating superuser with email: {email}')

        # Delete existing user with this email to avoid conflicts
        deleted, _ = User.objects.filter(email=email).delete()
        if deleted:
            self.stdout.write(f'Deleted {deleted} existing user(s) with email {email}')

        # Create superuser
        user = User.objects.create_superuser(
            email=email,
            username='mrdamrongsakn',
            password=password,
            first_name='Admin',
            last_name='User',
        )
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Verify the user can authenticate
        from django.contrib.auth import authenticate
        test_user = authenticate(username=email, password=password)
        if test_user:
            self.stdout.write(self.style.SUCCESS(f'SUCCESS: Superuser {email} created and verified!'))
        else:
            # Try with username
            test_user = authenticate(username='mrdamrongsakn', password=password)
            if test_user:
                self.stdout.write(self.style.SUCCESS(f'SUCCESS: Superuser {email} created (login with username)'))
            else:
                self.stdout.write(self.style.WARNING(f'WARNING: User created but authentication test failed'))

        # Print user details for debugging
        self.stdout.write(f'User ID: {user.id}')
        self.stdout.write(f'Username: {user.username}')
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Is staff: {user.is_staff}')
        self.stdout.write(f'Is superuser: {user.is_superuser}')
