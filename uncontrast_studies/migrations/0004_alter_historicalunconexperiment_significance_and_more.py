# Generated by Django 5.0.4 on 2024-05-22 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uncontrast_studies', '0003_alter_unconsciousnessmeasure_sub_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalunconexperiment',
            name='significance',
            field=models.CharField(choices=[('Negative', 'Negative'), ('Positive', 'Positive'), ('Mixed', 'Mixed')], default='Mixed', max_length=10),
        ),
        migrations.AlterField(
            model_name='unconexperiment',
            name='significance',
            field=models.CharField(choices=[('Negative', 'Negative'), ('Positive', 'Positive'), ('Mixed', 'Mixed')], default='Mixed', max_length=10),
        ),
    ]