from django.contrib import admin
from django.urls import path, include
from graphene_django.views import GraphQLView
from admin_theme_manager.schema import schema  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('admin_theme_manager.urls')), 
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]