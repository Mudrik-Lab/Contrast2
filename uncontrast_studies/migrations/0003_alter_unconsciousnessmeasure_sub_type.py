# Generated by Django 5.0.4 on 2024-05-10 12:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("uncontrast_studies", "0002_auto_20240405_1947"),
    ]

    operations = [
        migrations.AlterField(
            model_name="unconsciousnessmeasure",
            name="sub_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="unconsciousness_measures",
                to="uncontrast_studies.unconsciousnessmeasuresubtype",
            ),
        ),
    ]