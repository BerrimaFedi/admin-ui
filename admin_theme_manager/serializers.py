from rest_framework import serializers
from .models import AdminTheme

class AdminThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminTheme
        fields = ['id', 'name', 'css_url', 'js_url', 'is_active']

    def validate(self, data):
        css_url = data.get('css_url')
        js_url = data.get('js_url')

        if css_url and not css_url.endswith(('.css')):
            raise serializers.ValidationError({"css_url": "CSS URL must end with '.css'."})
        if js_url and not js_url.endswith(('.js')):
            raise serializers.ValidationError({"js_url": "JS URL must end with '.js'."})
        return data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if instance.is_active:
            AdminTheme.objects.exclude(pk=instance.pk).update(is_active=False)
        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        if instance.is_active:
            AdminTheme.objects.exclude(pk=instance.pk).update(is_active=False)
        return instance