# Generated by Django 5.0.1 on 2024-01-15 22:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_alter_profile_academic_stage"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="has_opted_for_contrast_updates",
            field=models.BooleanField(default=True),
        ),
    ]