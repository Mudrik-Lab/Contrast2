# Generated by Django 4.1.5 on 2023-01-12 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0006_stimuluscategory_findingtagtype_family_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stimulussubcategory",
            name="parent",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="studies.stimuluscategory"
            ),
        ),
    ]
