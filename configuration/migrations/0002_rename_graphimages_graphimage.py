# Generated by Django 4.2.1 on 2023-05-26 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GraphImages',
            new_name='GraphImage',
        ),
    ]