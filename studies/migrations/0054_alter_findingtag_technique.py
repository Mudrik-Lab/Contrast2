# Generated by Django 5.0.1 on 2024-02-03 13:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0053_alter_paradigm_parent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="findingtag",
            name="technique",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="findings_tags",
                to="studies.technique",
            ),
        ),
    ]