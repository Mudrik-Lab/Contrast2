# Generated by Django 5.0.2 on 2024-04-23 20:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("uncontrast_studies", "0008_remove_historicalunconspecificparadigm_experiment_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalunconexperiment",
            name="significance",
            field=models.PositiveIntegerField(
                blank=True, choices=[(1, "Negative"), (2, "Positive"), (3, "Mixed")], null=True
            ),
        ),
        migrations.AddField(
            model_name="historicalunconfinding",
            name="is_important",
            field=models.BooleanField(default=True, verbose_name="was the finding important"),
        ),
        migrations.AddField(
            model_name="unconexperiment",
            name="significance",
            field=models.PositiveIntegerField(
                blank=True, choices=[(1, "Negative"), (2, "Positive"), (3, "Mixed")], null=True
            ),
        ),
        migrations.AddField(
            model_name="unconfinding",
            name="is_important",
            field=models.BooleanField(default=True, verbose_name="was the finding important"),
        ),
        migrations.AlterField(
            model_name="unconsuppressionmethod",
            name="sub_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="suppression_methods",
                to="uncontrast_studies.unconsuppressionmethodsubtype",
            ),
        ),
        migrations.AlterField(
            model_name="unconsuppressionmethod",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="suppression_methods",
                to="uncontrast_studies.unconsuppressionmethodtype",
            ),
        ),
        migrations.AlterField(
            model_name="uncontask",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="tasks", to="uncontrast_studies.uncontasktype"
            ),
        ),
    ]