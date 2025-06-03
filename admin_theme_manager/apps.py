# admin_theme_manager/apps.py
from django.apps import AppConfig

class AdminThemeManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_theme_manager'
    verbose_name = 'Admin Theme Manager' # Optional: A more readable name for the admin

    def ready(self):
        # Import your tasks module here to ensure signals are registered
        import admin_theme_manager.tasks
