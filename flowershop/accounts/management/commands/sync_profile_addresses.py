from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Backfill UserProfile address fields from saved DeliveryAddress records.'

    def handle(self, *args, **options):
        synced_profiles = 0

        for user in User.objects.all().iterator():
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.sync_default_delivery_address()
            synced_profiles += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully synced profile address fields for {synced_profiles} user(s).'
            )
        )
