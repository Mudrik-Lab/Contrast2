# Generated by Django 4.1.5 on 2023-01-12 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0005_auto_20230109_1354"),
    ]

    operations = [
        migrations.CreateModel(
            name="StimulusCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name="findingtagtype",
            name="family",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="studies.findingtagfamily"
            ),
        ),
        migrations.CreateModel(
            name="StimulusSubCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50)),
                (
                    "parent",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="studies.stimuluscategory"),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="stimulus",
            name="category",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="studies.stimuluscategory"),
        ),
        migrations.AlterField(
            model_name="stimulus",
            name="sub_category",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="studies.stimulussubcategory"
            ),
        ),
    ]
