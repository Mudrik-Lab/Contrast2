import datetime
import json

from django.urls import reverse

from approval_process.choices import ApprovalChoices
from studies.choices import TypeOfConsciousnessChoices, ExperimentTypeChoices, TheoryDrivenChoices, ReportingChoices, \
    SampleChoices
from studies.models import Study
from contrast_api.tests.base import BaseTestCase


# Create your tests here.


class SubmittedStudiesViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_study_creation_by_user(self):
        """
        test study is created with 201
        test approval status is pending and approval process is created
        test submitter gets study back, but other user don't
        """
        self.given_user_exists(username="submitting_user")
        self.given_user_authenticated("submitting_user", "12345")
        study_res = self.when_study_created_by_user_via_api()

        res = self.get_pending_studies()
        self.assertEqual(len(res["results"]), 1)

        first_result = res["results"][0]
        res = self.get_specific_study(first_result["id"])
        self.assertEqual(res["approval_status"], ApprovalChoices.PENDING)

        self.assertIsNotNone(res["approval_process"])
        study = Study.objects.get(id=study_res["id"])
        self.assertEqual(study.approval_process.started_at.date(), datetime.date.today())

        experiments_res = self.get_experiments_for_study(first_result["id"])
        self.assertEqual(experiments_res["count"], 0)

        res_experiment = self.when_experiment_is_added_to_study_via_api(study_id=first_result["id"])

        self.assertListEqual(res_experiment["techniques"], ["EEG"])
        self.assertEqual(res_experiment["tasks"][0]["description"], "a task")

        experiments_res = self.get_experiments_for_study(first_result["id"])
        self.assertEqual(experiments_res["count"], 1)

    def when_study_created_by_user_via_api(self, **kwargs):
        default_study = dict(DOI="10.1016/j.cortex.2017.07.010", title="a study", year=1990,
                             corresponding_author_email="test@example.com",
                             authors=[],
                             authors_key_words=["key", "word"],
                             affiliations="some affiliations", countries=["IL"])
        study_params = {**default_study, **kwargs}

        target_url = reverse("studies-submitted-list")
        res = self.client.post(target_url, data=json.dumps(study_params), content_type="application/json")
        self.assertEqual(res.status_code, 201)
        return res.data

    def test_study_creation_and_update_flow(self):
        """
        test study is created with 201
        test approval status is pending and approval process is created
        test submitter gets study back, but other user don't
        """
        self.given_user_exists(username="submitting_user")
        self.given_user_authenticated("submitting_user", "12345")
        author1 = self.given_an_author_exists("author1")
        study_res = self.when_study_created_by_user_via_api(authors_key_words=[], authors=[author1.id])
        study_id = study_res["id"]
        self.assertEqual(study_res["authors"][0]["name"], author1.name)

        update_res = self.when_study_is_updated(study_id, authors_key_words=["what"], countries=["GB", "IL"])
        self.assertListEqual(update_res["countries"], ["GB", "IL"])
        self.assertEqual(update_res["authors"][0]["name"], author1.name)

        res = self.get_pending_studies()
        self.assertEqual(len(res["results"]), 1)

    def when_experiment_is_added_to_study_via_api(self, study_id: int, **kwargs):
        target_url = reverse("studies-experiments-list", args=[study_id])
        default_experiment = dict(
            finding_description="look what we found",
            is_reporting=ReportingChoices.NO_REPORT,
            theory_driven=TheoryDrivenChoices.POST_HOC,
            tasks=[dict(description="a task", type="Deviant Detection")],
            samples=[dict(total_size=10, size_included=5, type=SampleChoices.CHILDREN)],
            stimuli=[],
            measures=[],
            interpretations=[],
            finding_tags=[],
            consciousness_measures=[],
            type=ExperimentTypeChoices.NEUROSCIENTIFIC,
            techniques=["EEG"],
            paradigms=["Blindsight (Abnormal Contents of Consciousness)"],
            theory_driven_theories=["GNW"],
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT)
        experiment_params = {**default_experiment, **kwargs}
        res = self.client.post(target_url, data=json.dumps(experiment_params), content_type="application/json")
        self.assertEqual(res.status_code, 201)
        return res.data

    def get_pending_studies(self):
        target_url = reverse("studies-submitted-list")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, 200)
        return res.data

    def get_specific_study(self, study_id):
        target_url = reverse("studies-submitted-detail", args=[study_id])
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, 200)
        return res.data

    def get_experiments_for_study(self, study_id):
        target_url = reverse("studies-experiments-list", args=[study_id])
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, 200)
        return res.data

    def when_study_is_updated(self, study_id, **kwargs):
        target_url = reverse("studies-submitted-detail", args=[study_id])
        res = self.client.patch(target_url, data=json.dumps(kwargs), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        return res.data
