from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi, renderers
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Diploma Project API",
      default_version='v1',
      description="""
      Complete API documentation for the Diploma Backend project.
      
      ## Authentication
      This API uses JWT token authentication. Most endpoints require an Authorization header with the format:
      `Bearer <token>`
      
      ## Token Acquisition
      1. Register a new account at `/api/users/register/`
      2. Login at `/api/users/login/` to get `access` and `refresh` tokens
      3. Use the `access` token in the Authorization header
      4. When the access token expires, use the `refresh` token at `/api/users/token/refresh/` to get a new access token
      """,
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="admin@diploma.example.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/topics/', include('topics.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("api/", include("chat.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Additional formats available
urlpatterns += [
    # JSON and YAML formats
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]