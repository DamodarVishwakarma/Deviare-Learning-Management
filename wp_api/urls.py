from django.urls import path, include
from wp_api import views

urlpatterns = [
    path("wc_hook/", views.wc_hook),
]