from django.urls import path

from .views import ChatDocumentView, ChatHomeView, ChatHistoryView


app_name = "chat"

urlpatterns = [
    path("chat/", ChatHomeView.as_view(), name="home"),
    path("chat/document/<int:document_id>/", ChatDocumentView.as_view(), name="document"),
    path("history/", ChatHistoryView.as_view(), name="history"),
]
