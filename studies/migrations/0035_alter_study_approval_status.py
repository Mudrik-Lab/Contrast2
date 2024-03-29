# Generated by Django 4.2.2 on 2023-06-26 10:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0034_alter_study_approval_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="study",
            name="approval_status",
            field=models.IntegerField(
                choices=[(0, "Pending"), (3, "Awaiting Review"), (1, "Approved"), (2, "Rejected")], default=0
            ),
        ),
    ]
