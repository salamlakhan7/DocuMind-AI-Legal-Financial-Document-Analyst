import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_documentprocessing"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentChunk",
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
                ("chunk_index", models.PositiveIntegerField()),
                ("page_number", models.PositiveIntegerField()),
                ("content", models.TextField()),
                ("character_count", models.PositiveIntegerField()),
                ("word_count", models.PositiveIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chunks",
                        to="documents.document",
                    ),
                ),
            ],
            options={
                "ordering": ["chunk_index"],
            },
        ),
        migrations.AddConstraint(
            model_name="documentchunk",
            constraint=models.UniqueConstraint(
                fields=("document", "chunk_index"),
                name="unique_document_chunk_index",
            ),
        ),
    ]
