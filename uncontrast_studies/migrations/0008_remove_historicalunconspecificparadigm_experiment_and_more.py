# Generated by Django 5.0.2 on 2024-04-12 18:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("uncontrast_studies", "0007_alter_uncontask_experiment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalunconspecificparadigm",
            name="experiment",
        ),
        migrations.RemoveField(
            model_name="unconspecificparadigm",
            name="experiment",
        ),
    ]