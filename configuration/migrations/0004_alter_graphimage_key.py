# Generated by Django 4.2.7 on 2023-12-20 07:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("configuration", "0003_auto_20230526_2203"),
    ]

    operations = [
        migrations.AlterField(
            model_name="graphimage",
            name="key",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
