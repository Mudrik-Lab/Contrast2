# Generated by Django 4.2.4 on 2023-09-03 08:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0045_experiment_paradigms_notes_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='experiment',
            old_name='notes',
            new_name='sample_notes',
        ),
    ]