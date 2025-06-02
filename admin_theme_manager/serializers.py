from rest_framework import serializers
from .models import AdminTheme

class AdminThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminTheme
        fields = '__all__'
