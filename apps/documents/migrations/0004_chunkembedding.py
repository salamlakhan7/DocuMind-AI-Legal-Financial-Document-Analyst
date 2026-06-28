import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0003_documentchunk"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChunkEmbedding",
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
                ("model_name", models.CharField(max_length=255)),
                ("vector_dimension", models.PositiveIntegerField()),
                ("embedding_created_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "chunk",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="embedding",
                        to="documents.documentchunk",
                    ),
                ),
            ],
            options={
                "ordering": ["chunk__document", "chunk__chunk_index"],
            },
        ),
    ]
