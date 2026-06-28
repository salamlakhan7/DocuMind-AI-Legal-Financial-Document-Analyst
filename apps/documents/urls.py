from django.urls import path

from .views import (
    DocumentDeleteView,
    DocumentDetailView,
    DocumentAskView,
    DocumentListView,
    DocumentRetrieveView,
    DocumentUploadView,
)


app_name = "documents"

urlpatterns = [
    path("documents/", DocumentListView.as_view(), name="list"),
    path("documents/upload/", DocumentUploadView.as_view(), name="upload"),
    path("documents/<int:pk>/", DocumentDetailView.as_view(), name="detail"),
    path("documents/<int:pk>/ask/", DocumentAskView.as_view(), name="ask"),
    path("documents/<int:pk>/retrieve/", DocumentRetrieveView.as_view(), name="retrieve"),
    path("documents/<int:pk>/delete/", DocumentDeleteView.as_view(), name="delete"),
]
