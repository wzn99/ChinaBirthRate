# Generated by Django 4.1.7 on 2023-06-14 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("populationdata", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuestionIndex",
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
                ("question_keyword", models.CharField(max_length=256)),
                ("question_doclist", models.TextField()),
            ],
        ),
    ]
