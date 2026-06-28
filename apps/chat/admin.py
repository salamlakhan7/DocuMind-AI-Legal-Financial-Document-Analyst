from django.contrib import admin

from .models import ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "document", "updated_at", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "user__username", "document__title")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "model_name", "created_at")
    list_filter = ("role", "model_name", "created_at")
    search_fields = ("content", "session__title", "session__document__title")
