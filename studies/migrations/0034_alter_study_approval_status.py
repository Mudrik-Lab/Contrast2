# Generated by Django 4.2.1 on 2023-06-14 16:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0033_auto_20230517_1023"),
    ]

    operations = [
        migrations.AlterField(
            model_name="study",
            name="approval_status",
            field=models.IntegerField(
                choices=[(0, "Pending"), (3, "In Process"), (1, "Approved"), (2, "Rejected")], default=0
            ),
        ),
    ]
