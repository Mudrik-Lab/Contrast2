# Generated by Django 4.1.4 on 2023-01-09 16:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0012_remove_study_abstract_remove_study_publisher_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="study",
            old_name="key_words",
            new_name="authors_key_words",
        ),
        migrations.RemoveField(
            model_name="study",
            name="link",
        ),
    ]
