# Generated by Django 5.0.3 on 2024-03-12 13:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0056_alter_historicalstudy_type_alter_study_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stimulus",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="stimuli", to="studies.stimuluscategory"
            ),
        ),
        migrations.AlterField(
            model_name="stimulus",
            name="modality",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="stimuli", to="studies.modalitytype"
            ),
        ),
        migrations.AlterField(
            model_name="stimulus",
            name="sub_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="stimuli",
                to="studies.stimulussubcategory",
            ),
        ),
    ]
