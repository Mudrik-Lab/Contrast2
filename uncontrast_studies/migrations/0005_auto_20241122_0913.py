# Generated by Django 5.1.2 on 2024-11-22 09:13

from django.db import migrations


def bootstrap_both_measure_type(apps, schema_editor):
    UnConsciousnessMeasureType = apps.get_model("uncontrast_studies", "UnConsciousnessMeasureType")
    UnConsciousnessMeasureType.objects.get_or_create(name="Both")


class Migration(migrations.Migration):
    dependencies = [
        ("uncontrast_studies", "0004_alter_historicalunconsample_type_and_more"),
    ]

    operations = [migrations.RunPython(bootstrap_both_measure_type, reverse_code=migrations.RunPython.noop)]