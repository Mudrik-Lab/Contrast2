import json

from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from typing import Optional
from approval_process.choices import ApprovalChoices
from studies.choices import TypeOfConsciousnessChoices, ReportingChoices, TheoryDrivenChoices, ExperimentTypeChoices
from studies.models import (
    Experiment,
    Theory,
    Interpretation,
    Paradigm,
    Measure,
    MeasureType,
    TaskType,
    Task,
    Technique,
    Study,
    FindingTag,
    Sample,
    Author,
)


class BaseTestCase(APITestCase):
    def given_study_exists(self, **kwargs) -> Study:
        default_study = dict(
            DOI="10.1016/j.cortex.2017.07.010",
            title="a study",
            year=1990,
            corresponding_author_email="test@example.com",
            approval_status=ApprovalChoices.APPROVED,
            authors_key_words=["key", "word"],
            affiliations="some affiliations",
            countries=["IL"],
        )
        study_params = {**default_study, **kwargs}
        study, created = Study.objects.get_or_create(**study_params)
        return study

    def given_user_authenticated(self, username, password):
        auth_url = reverse("api-token-obtain-pair")
        res = self.client.post(auth_url, data=dict(username=username, password=password))
        access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

    def given_experiment_exists_for_study(self, study, **kwargs) -> Experiment:
        default_experiment = dict(
            study=study,
            results_summary="look what we found",
            is_reporting=ReportingChoices.NO_REPORT,
            theory_driven=kwargs.get("theory_driven", TheoryDrivenChoices.POST_HOC),
            type=ExperimentTypeChoices.NEUROSCIENTIFIC,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
        )
        paradigms = None
        techniques = None
        theory_driven_theories = None
        finding_tags = None
        samples = None
        if "paradigms" in kwargs:
            paradigms = kwargs.pop("paradigms")

        if "techniques" in kwargs:
            techniques = kwargs.pop("techniques")

        if "finding_tags" in kwargs:
            finding_tags = kwargs.pop("finding_tags")

        if "theory_driven_theories" in kwargs:
            theory_driven_theories = kwargs.pop("theory_driven_theories")

        if "samples" in kwargs:
            samples = kwargs.pop("samples")

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

        if samples:
            for sample in samples:
                sample = Sample.objects.create(**dict(experiment=experiment, **sample))
                experiment.samples.add(sample)

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
        url = f"{url}?{params}"
        return url

    def given_theory_exists(self, name: str, parent: Theory = None, acronym: str = None):
        theory, created = Theory.objects.get_or_create(parent=parent, name=name, acronym=acronym)
        return theory

    def given_interpretation_exist(self, experiment: Experiment, theory: Theory, interpretation_type: str):
        interpretation, created = Interpretation.objects.get_or_create(
            experiment=experiment, theory=theory, type=interpretation_type
        )
        return interpretation

    def given_paradigm_exists(self, name: str, parent: Optional[Paradigm] = None):
        params = dict(name=name, parent=parent, sub_type=None)
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

    def given_user_exists(self, username, password="12345", is_staff=False, is_superuser=False, **kwargs):
        obj = get_user_model().objects.create_user(
            username=username, password=password, is_staff=is_staff, is_superuser=is_superuser, **kwargs
        )

        return obj

    def when_user_logs_in(self, username, password):
        auth_url = reverse("api-token-obtain-pair")
        res = self.client.post(auth_url, data=dict(username=username, password=password))
        return res

    def when_user_access_home(self):
        res = self.client.get(reverse("profiles-home"))
        return res

    def when_user_does_username_check(self, username):
        res = self.client.post(reverse("profiles-check-username"), data=dict(username=username))
        return res

    def when_user_requests_password_reset(self, email):
        auth_url = reverse("profiles-request-password-reset")
        res = self.client.post(auth_url, data=dict(email=email))
        return res

    def verify_no_email_was_sent_to_user(self, email: str):
        for message in mail.outbox:
            if message.to[0] == email:
                raise AssertionError(f"Expected {email} not to exist but it does")

    def verify_email_was_sent_to_user(self, email):
        for message in mail.outbox:
            if message.to[0] == email:
                return True
        raise AssertionError(f"Expected {email} to exist but it doesn't")

    def when_user_resets_password(self, token, password, email):
        auth_url = reverse("profiles-reset-password")
        res = self.client.post(auth_url, data=dict(email=email, token=token, password=password))
        return res

    def when_user_is_registered(self, **kwargs):
        data = dict(**kwargs)
        res = self.client.post(
            reverse("profiles-register-user"), data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def given_an_author_exists(self, name: str) -> Author:
        auther, created = Author.objects.get_or_create(name=name)
        return auther

    def when_a_user_creates_an_auther(self, name: str):
        res = self.client.post(reverse("authors-list"), data=dict(name=name))
        return res

    def when_a_user_searches_for_author(self, part_name: str):
        res = self.client.get(self.reverse_with_query_params("authors-list", search=part_name))
        return res
