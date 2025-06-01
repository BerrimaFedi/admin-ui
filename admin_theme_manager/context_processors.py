from .models import AdminTheme

def admin_theme(request):
    try:
        active_theme = AdminTheme.objects.get(is_active=True)
        return {'active_theme': active_theme}
    except AdminTheme.DoesNotExist:
        return {'active_theme': None}