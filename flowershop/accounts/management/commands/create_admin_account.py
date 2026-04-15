from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Create or update a dedicated admin-only account safely.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--email', required=True)
        parser.add_argument('--password', required=True)

    def handle(self, *args, **options):
        user_model = get_user_model()
        username = options['username'].strip()
        email = options['email'].strip().lower()
        password = options['password']

        if not username or not email or not password:
            raise CommandError('Username, email, and password are required.')

        try:
            validate_password(password)
        except ValidationError as exc:
            raise CommandError(exc.messages[0])

        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )

        if not created and user.email != email:
            raise CommandError('That username already exists with a different email address.')

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} admin account: {username}'))
