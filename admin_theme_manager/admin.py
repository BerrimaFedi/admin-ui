from django.contrib import admin
from .models import AdminTheme
from django import forms

class AdminThemeForm(forms.ModelForm):
    class Meta:
        model = AdminTheme
        fields = '__all__'

    def clean_css_url(self):
        url = self.cleaned_data['css_url']
        if not url.endswith('.css'):
            raise forms.ValidationError('Must end with .css')
        return url

    def clean_js_url(self):
        url = self.cleaned_data['js_url']
        if url and not url.endswith('.js'):
            raise forms.ValidationError('Must end with .js')
        return url

class AdminThemeAdmin(admin.ModelAdmin):
    form = AdminThemeForm
    list_display = ('name', 'css_url', 'js_url', 'is_active')
    list_editable = ('is_active',)

admin.site.register(AdminTheme, AdminThemeAdmin)