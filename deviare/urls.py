from django.contrib import admin
from django.urls import path, include
from main import views as main_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url


old_urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"main/", include("main.urls")),
    path(r"project/", include("project.urls")),
    path(r"services/", include("services.urls")),

    path(r"read_mail_api", main_views.read_mail_api, name="read-mail-api"),
    path(r"read_outlook_mail", main_views.read_outlook_mail),
    path(r"outlook_mail", main_views.outlook_mail),
    path(r"api/", include("wp_api.urls")),

]
apps_url_patterns = [
    path(r"main/", include("main.urls")),
    path(r"project/", include("project.urls")),
    path(r"services/", include("services.urls")),
    path(r"api/", include("wp_api.urls")),
]
schema_view = get_schema_view(
    openapi.Info(
        title="Deviare Enterprise Platform API",
        default_version='v2.0.1',
        description="Enterprise Platform API endpoints V2",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ryan.kanes@deviare.africa"),
        license=openapi.License(name="Private License"),
    ),
    patterns=apps_url_patterns,
    public=True,
    # permission_classes=(permissions.IsAdminUser,),
)


urlpatterns = old_urlpatterns + [

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]