from .models import AdminTheme

def active_theme(request):  # Changed function name to active_theme
    theme = AdminTheme.objects.filter(is_active=True).first()
    return {
        "active_theme": theme,  # Changed key to active_theme to match template
        "theme_css": theme.css_url if theme else "",
        "theme_js": theme.js_url if theme and theme.js_url else ""
    }