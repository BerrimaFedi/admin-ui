from django.db import models
from django.core.exceptions import ValidationError
from django.db import models

class AdminTheme(models.Model):
    name = models.CharField(max_length=100, unique=True)
    css_url = models.CharField(max_length=255, blank=True, null=True)
    js_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    accessibility_report = models.TextField(blank=True, null=True)
    ui_suggestions = models.JSONField(blank=True, null=True)  

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}
        if self.css_url and not self.css_url.endswith('.css'):
            errors['css_url'] = "CSS URL must end with .css"
        if self.js_url and self.js_url and not self.js_url.endswith('.js'):
            errors['js_url'] = "JS URL must end with .js"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        if self.is_active:
            AdminTheme.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

