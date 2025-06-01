from django.db import models
#from django.core.validators import URLValidator  # Remove or change this

class AdminTheme(models.Model):
    name = models.CharField(max_length=100, unique=True)
    css_url = models.CharField(max_length=255, blank=True, null=True)  # Removed URLValidator
    js_url = models.CharField(max_length=255, blank=True, null=True)  # Removed URLValidator
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Admin Theme"
        verbose_name_plural = "Admin Themes"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            AdminTheme.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)