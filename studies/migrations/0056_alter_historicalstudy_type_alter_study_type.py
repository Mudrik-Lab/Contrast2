# Generated by Django 5.0.2 on 2024-03-11 07:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0055_historicalstudy_type_study_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalstudy",
            name="type",
            field=models.CharField(
                choices=[("Consciousness", "Consciousness"), ("UnConsciousness", "Unconsciousness")],
                default="Consciousness",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="study",
            name="type",
            field=models.CharField(
                choices=[("Consciousness", "Consciousness"), ("UnConsciousness", "Unconsciousness")],
                default="Consciousness",
                max_length=20,
            ),
        ),
    ]