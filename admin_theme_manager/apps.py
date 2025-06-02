from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AdminThemeManagerConfig(AppConfig):
    name = 'admin_theme_manager'
    verbose_name = _('Admin Theme Manager')

    def ready(self):
        import admin_theme_manager.signals