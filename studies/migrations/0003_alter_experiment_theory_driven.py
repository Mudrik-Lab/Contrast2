# Generated by Django 4.1.4 on 2023-01-04 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0002_alter_experiment_finding_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='theory_driven',
            field=models.CharField(choices=[('driven', 'Driven'), ('mentioning', 'Mentioning'), ('post-hoc', 'Post hoc')], max_length=20),
        ),
    ]