# Generated by Django 4.2.4 on 2023-09-04 15:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0046_rename_notes_experiment_sample_notes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experiment",
            name="results_summary",
            field=models.TextField(blank=True, null=True),
        ),
    ]
