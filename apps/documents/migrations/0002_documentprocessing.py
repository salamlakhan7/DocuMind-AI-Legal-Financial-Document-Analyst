import django.db.models.deletion
from django.db import migrations, models


def create_processing_records(apps, schema_editor):
    Document = apps.get_model("documents", "Document")
    DocumentProcessing = apps.get_model("documents", "DocumentProcessing")

    for document in Document.objects.all():
        DocumentProcessing.objects.get_or_create(document=document)


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentProcessing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("processing_time_ms", models.PositiveIntegerField(blank=True, null=True)),
                ("processing_version", models.CharField(default="v1", max_length=20)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="processing",
                        to="documents.document",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.RunPython(create_processing_records, migrations.RunPython.noop),
    ]
