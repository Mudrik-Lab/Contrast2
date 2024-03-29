# Generated by Django 4.1.4 on 2022-12-30 18:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ApprovalProcess",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.SmallIntegerField(choices=[(0, "Pending"), (1, "Approved"), (2, "Rejected")], default=0),
                ),
                ("exclusion_reason", models.TextField(blank=True, null=True)),
                ("research_area", models.CharField(blank=True, max_length=50, null=True)),
                ("sub_research_area", models.CharField(blank=True, max_length=50, null=True)),
                ("reviewers", models.ManyToManyField(related_name="approvals", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="ApprovalComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "process",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="approval_process.approvalprocess",
                    ),
                ),
                (
                    "reviewer",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
    ]
