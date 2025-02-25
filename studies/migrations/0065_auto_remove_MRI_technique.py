# Generated by Django 5.1.5 on 2025-02-10 14:59
from django.db import migrations

import logging

from studies.services.get_queryset_to_modify import get_queryset_to_modify

logger = logging.getLogger("Contrast2")


def remove_redundant_mri_techniques_from_experiments(apps, schema_editor):
    """
    Data migration to remove 'MRI' technique from experiments
    that should have only 'fMRI' technique.

    """
    MAX_EXPERIMENT_ID = 988  # the highest id of pre-existing experiments
    true_mri_and_fmri_experiments_ids = [714]
    Experiment = apps.get_model("studies", "Experiment")
    Technique = apps.get_model("studies", "Technique")
    FindingTag = apps.get_model("studies", "FindingTag")

    try:
        fmri_technique = Technique.objects.get(name="fMRI")
    except Technique.DoesNotExist:
        raise Exception("Required technique 'fMRI' not found")
    try:
        mri_technique = Technique.objects.get(name="MRI")
    except Technique.DoesNotExist:
        raise Exception("Required technique 'fMRI' not found")

    experiments_to_modify = get_queryset_to_modify(
        experiment_model=Experiment,
        max_id=MAX_EXPERIMENT_ID,
        safe_list=true_mri_and_fmri_experiments_ids,
        first_technique=fmri_technique,
        second_technique=mri_technique,
    )

    for experiment in experiments_to_modify:
        experiment.techniques.remove(mri_technique)
        experiment.save()
        logger.info(f"Removed MRI technique from Experiment {experiment.id}")

    experiment_count = experiments_to_modify.count()
    logger.info(f"Migration completed. Modified {experiment_count} experiments")

    findings_to_modify = FindingTag.objects.filter(experiment__in=experiments_to_modify)

    for finding in findings_to_modify:
        if finding.techniques__isnull:
            finding.techniques.add(fmri_technique)


class Migration(migrations.Migration):
    dependencies = [
        ("studies", "0064_auto_populate_AAL_atlas_tags"),
    ]

    operations = [
        migrations.RunPython(remove_redundant_mri_techniques_from_experiments),
    ]
