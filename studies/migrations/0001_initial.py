# Generated by Django 4.1.4 on 2022-12-28 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('approval_process', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('approval_status', models.IntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Rejected')], default=0)),
                ('approval_process', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='approval_process.approvalprocess')),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiments', to='studies.study')),
            ],
        ),
    ]