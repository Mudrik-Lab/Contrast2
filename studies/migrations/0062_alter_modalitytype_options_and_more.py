# Generated by Django 5.1.3 on 2024-12-12 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0061_auto_20241026_1234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modalitytype',
            options={'ordering': [models.Case(models.When(name='None', then=models.Value(0)), default=models.Value(1)), 'name'], 'verbose_name_plural': 'stimulus modalities'},
        ),
        migrations.AlterModelOptions(
            name='stimuluscategory',
            options={'ordering': [models.Case(models.When(name='None', then=models.Value(0)), default=models.Value(1)), 'name'], 'verbose_name_plural': 'stimulus categories'},
        ),
        migrations.AlterModelOptions(
            name='stimulussubcategory',
            options={'ordering': [models.Case(models.When(name='None', then=models.Value(0)), default=models.Value(1)), 'name'], 'verbose_name_plural': 'stimulus sub categories'},
        ),
    ]