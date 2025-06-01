from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AdminTheme
from .tasks import compile_scss, deploy_static_assets, analyze_ui_suggestions

@receiver(post_save, sender=AdminTheme)
def handle_admin_theme_save(sender, instance, **kwargs):
    if instance.css_url and instance.css_url.endswith('.scss'):
        scss_filepath = instance.css_url
        css_filepath = instance.css_url[:-5] + '.css'
        compile_scss.delay(scss_filepath, css_filepath)
    deploy_static_assets.delay()
    if instance.css_url and instance.css_url.endswith('.css'):
        analyze_ui_suggestions.delay(instance.css_url)