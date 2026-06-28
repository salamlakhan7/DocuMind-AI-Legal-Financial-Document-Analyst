from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Document, DocumentProcessing


@receiver(post_save, sender=Document)
def create_document_processing(sender, instance, created, **kwargs):
    if created:
        DocumentProcessing.objects.get_or_create(document=instance)
