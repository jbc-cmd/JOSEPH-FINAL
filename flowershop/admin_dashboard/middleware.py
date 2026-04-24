from django.utils import timezone


class LastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            last_tracked = request.session.get('last_activity_tracked_at')
            now = timezone.now()
            should_update = True
            if last_tracked:
                previous = timezone.datetime.fromisoformat(last_tracked)
                if timezone.is_naive(previous):
                    previous = timezone.make_aware(previous, timezone.get_current_timezone())
                should_update = (now - previous).total_seconds() >= 300

            if should_update:
                request.user.profile.__class__.objects.filter(pk=request.user.profile.pk).update(last_active_at=now)
                request.session['last_activity_tracked_at'] = now.isoformat()

        return response
