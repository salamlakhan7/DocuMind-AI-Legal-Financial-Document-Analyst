import apps.documents.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
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
                ("title", models.CharField(max_length=255)),
                (
                    "file",
                    models.FileField(
                        upload_to="documents/",
                        validators=[apps.documents.models.validate_pdf_upload],
                    ),
                ),
                ("original_filename", models.CharField(max_length=255)),
                ("file_size", models.PositiveIntegerField()),
                ("file_type", models.CharField(max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("uploaded", "Uploaded"),
                            ("processing", "Processing"),
                            ("ready", "Ready"),
                            ("failed", "Failed"),
                        ],
                        default="uploaded",
                        max_length=20,
                    ),
                ),
                ("page_count", models.PositiveIntegerField(blank=True, null=True)),
                ("chunk_count", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
