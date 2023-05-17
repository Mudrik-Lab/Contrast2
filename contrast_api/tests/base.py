from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from typing import Optional
from approval_process.choices import ApprovalChoices
from studies.choices import TypeOfConsciousnessChoices, ReportingChoices, TheoryDrivenChoices, \
    ExperimentTypeChoices
from studies.models import Experiment, Theory, Interpretation, Paradigm, Measure, MeasureType, TaskType, Task, \
    Technique, Study, FindingTag


class BaseTestCase(APITestCase):
    def given_study_exists(self, **kwargs) -> Study:
        default_study = dict(DOI="10.1016/j.cortex.2017.07.010", title="a study", year=1990,
                             corresponding_author_email="test@example.com",
                             approval_status=ApprovalChoices.APPROVED, authors_key_words=["key", "word"],
                             affiliations="some affiliations", countries=["IL"])
        study_params = {**default_study, **kwargs}
        study, created = Study.objects.get_or_create(**study_params)
        return study

    def given_experiment_exists_for_study(self, study, **kwargs) -> Experiment:
        default_experiment = dict(study=study,
                                  finding_description="look what we found",
                                  is_reporting=ReportingChoices.NO_REPORT,
                                  theory_driven=kwargs.get("theory_driven", TheoryDrivenChoices.POST_HOC),
                                  type=ExperimentTypeChoices.NEUROSCIENTIFIC,
                                  type_of_consciousness=TypeOfConsciousnessChoices.CONTENT)
        paradigms = None
        techniques = None
        theory_driven_theories = None
        finding_tags = None
        if "paradigms" in kwargs:
            paradigms = kwargs.pop("paradigms")

        if "techniques" in kwargs:
            techniques = kwargs.pop("techniques")

        if "finding_tags" in kwargs:
            finding_tags = kwargs.pop("finding_tags")

        if "theory_driven_theories" in kwargs:
            theory_driven_theories = kwargs.pop("theory_driven_theories")

        experiment_params = {**default_experiment, **kwargs}
        experiment, created = Experiment.objects.get_or_create(**experiment_params)
        if paradigms:
            for item in paradigms:
                experiment.paradigms.add(item)

        if techniques:
            for item in techniques:
                experiment.techniques.add(item)
        if theory_driven_theories:
            for item in theory_driven_theories:
                experiment.theory_driven_theories.add(item)

        if finding_tags:
            for item in finding_tags:
                tag = FindingTag.objects.create(**dict(experiment=experiment, **item))
                experiment.finding_tags.add(tag)

        return experiment

    def reverse_with_query_params(self, url_name: str, *args, **queryparams) -> str:
        parts = []
        for k, v in queryparams.items():
            if isinstance(v, list):
                part = "&".join([f"{k}={v_item}" for v_item in v])
            else:
                part = f"{k}={v}"
            parts.append(part)
        params = "&".join(parts)
        url = reverse(url_name, args=args)
        url = f'{url}?{params}'
        return url

    def given_theory_exists(self, name: str, parent: Theory = None, acronym: str = None):
        theory, created = Theory.objects.get_or_create(parent=parent, name=name, acronym=acronym)
        return theory

    def given_interpretation_exist(self, experiment: Experiment, theory: Theory, interpretation_type: str):
        interpretation, created = Interpretation.objects.get_or_create(experiment=experiment, theory=theory,
                                                                       type=interpretation_type)
        return interpretation

    def given_paradigm_exists(self, name: str, parent: Optional[Paradigm] = None):
        params = dict(name=name, parent=parent)
        paradigm, created = Paradigm.objects.get_or_create(**params)
        return paradigm

    def given_technique_exists(self, name: str):
        params = dict(name=name)
        technique, created = Technique.objects.get_or_create(**params)
        return technique

    def given_measure_exists(self, experiment_id, measure_type, notes: Optional[str] = None):
        measure_type_instance, created = MeasureType.objects.get_or_create(name=measure_type)
        params = dict(experiment_id=experiment_id, type=measure_type_instance, notes=notes)

        measure, created = Measure.objects.get_or_create(**params)
        return measure

    def given_task_exists(self, experiment_id, task_type, description: Optional[str] = None):
        task_type_instance, created = TaskType.objects.get_or_create(name=task_type)
        params = dict(experiment_id=experiment_id, type=task_type_instance, description=description)

        task, created = Task.objects.get_or_create(**params)
        return task
