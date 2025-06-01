from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import AdminTheme
from .serializers import AdminThemeSerializer

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
        return Response(serializer.data)

class UploadThemeView(generics.CreateAPIView):
    serializer_class = AdminThemeSerializer  # You might need a specific serializer for uploads
    permission_classes = [IsSuperUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # Implement logic to handle file uploads and create/update AdminTheme instance
        # You'll need to decide how you want to store and link uploaded themes
        return Response({"message": "Upload functionality to be implemented"})