from django.urls import path

from .views import (
    DashboardView,
    HomeView,
    SettingsView,
)


app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("settings/", SettingsView.as_view(), name="settings"),
]
