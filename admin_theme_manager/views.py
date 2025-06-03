from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
from .models import AdminTheme
from .serializers import AdminThemeSerializer
import os

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class AdminThemeListCreateView(generics.ListCreateAPIView):
    queryset = AdminTheme.objects.all()
    serializer_class = AdminThemeSerializer
    permission_classes = [IsSuperUser]

class AdminThemeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminTheme.objects.all()
    serializer_class = AdminThemeSerializer
    permission_classes = [IsSuperUser]

class ApplyThemeView(generics.UpdateAPIView):
    queryset = AdminTheme.objects.all()
    serializer_class = AdminThemeSerializer
    permission_classes = [IsSuperUser]
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={'is_active': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Ensure only the current theme is active
        AdminTheme.objects.exclude(pk=instance.pk).update(is_active=False)
        return Response(serializer.data)

class UploadThemeView(generics.CreateAPIView):
    serializer_class = AdminThemeSerializer  # We'll adapt this
    permission_classes = [IsSuperUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        css_file = request.FILES.get('css_file')
        js_file = request.FILES.get('js_file')

        if not name:
            return Response({"error": "Theme name is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not css_file:
            return Response({"error": "CSS file is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not css_file.name.endswith('.css'):
            return Response({"error": "CSS file must have a .css extension."}, status=status.HTTP_400_BAD_REQUEST)

        if js_file and not js_file.name.endswith('.js'):
            return Response({"error": "JS file must have a .js extension."}, status=status.HTTP_400_BAD_REQUEST)

        theme_exists = AdminTheme.objects.filter(name=name).exists()
        if theme_exists and not request.data.get('overwrite'):
            return Response({"error": f"Theme with name '{name}' already exists. Use 'overwrite=true' to replace."}, status=status.HTTP_409_CONFLICT)

        try:
            css_filename = default_storage.save(os.path.join('theming', css_file.name), css_file)
            css_url = default_storage.url(css_filename)

            js_url = None
            if js_file:
                js_filename = default_storage.save(os.path.join('theming', js_file.name), js_file)
                js_url = default_storage.url(js_filename)

            if theme_exists and request.data.get('overwrite'):
                theme = AdminTheme.objects.get(name=name)
                # Delete old files if they exist and are managed by Django storage
                if theme.css_url and theme.css_url.startswith(settings.MEDIA_URL):
                    old_css_path = default_storage.path(theme.css_url.replace(settings.MEDIA_URL, '', 1))
                    if default_storage.exists(old_css_path):
                        default_storage.delete(old_css_path)
                if theme.js_url and theme.js_url.startswith(settings.MEDIA_URL):
                    old_js_path = default_storage.path(theme.js_url.replace(settings.MEDIA_URL, '', 1))
                    if default_storage.exists(old_js_path):
                        default_storage.delete(old_js_path)

                serializer = AdminThemeSerializer(theme, data={'name': name, 'css_url': css_url, 'js_url': js_url}, partial=True)
            else:
                serializer = AdminThemeSerializer(data={'name': name, 'css_url': css_url, 'js_url': js_url})

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Clean up uploaded files on error
            if 'css_filename' in locals() and default_storage.exists(css_filename):
                default_storage.delete(css_filename)
            if 'js_filename' in locals() and default_storage.exists(js_filename):
                default_storage.delete(js_filename)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)