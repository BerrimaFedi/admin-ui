from django.urls import path
from .views import AdminThemeListCreateView, AdminThemeRetrieveUpdateDestroyView, ApplyThemeView, UploadThemeView

urlpatterns = [
    path('themes/', AdminThemeListCreateView.as_view(), name='admin-theme-list-create'),
    path('themes/<int:pk>/', AdminThemeRetrieveUpdateDestroyView.as_view(), name='admin-theme-retrieve-update-destroy'),
    path('themes/<int:pk>/apply/', ApplyThemeView.as_view(), name='admin-theme-apply'),
    path('themes/upload/', UploadThemeView.as_view(), name='admin-theme-upload'),
]