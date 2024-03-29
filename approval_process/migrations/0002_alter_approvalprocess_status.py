# Generated by Django 4.2.1 on 2023-06-14 16:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approval_process", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="approvalprocess",
            name="status",
            field=models.SmallIntegerField(
                choices=[(0, "Pending"), (3, "In Process"), (1, "Approved"), (2, "Rejected")], default=0
            ),
        ),
    ]
