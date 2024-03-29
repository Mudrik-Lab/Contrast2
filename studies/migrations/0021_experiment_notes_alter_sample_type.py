# Generated by Django 4.1.6 on 2023-02-16 21:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0020_auto_20230208_2326"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiment",
            name="notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="sample",
            name="type",
            field=models.CharField(
                choices=[
                    ("healthy_adults", "Healthy_adults"),
                    ("Healthy_college_students", "Healthy_college_students"),
                    ("children", "Children"),
                    ("patients", "Patients"),
                    ("non_human", "Non_human"),
                    ("computer", "Computer"),
                ],
                max_length=30,
            ),
        ),
    ]
