from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in
        from django.utils import timezone

        def update_last_login_with_queryset(sender, user, **kwargs):
            get_user_model().objects.filter(pk=user.pk).update(last_login=timezone.now())

        user_logged_in.disconnect(update_last_login)
        user_logged_in.connect(
            update_last_login_with_queryset,
            dispatch_uid='accounts.update_last_login_with_queryset',
        )
