import datetime
import json
from unittest import skip

from django.urls import reverse
from rest_framework import status

from approval_process.choices import ApprovalChoices
from contrast_api.choices import (
    ExperimentTypeChoices,
    InterpretationsChoices,
)
from studies.models import Study
from contrast_api.tests.base import BaseTestCase
from uncontrast_studies.tests.base import UnContrastBaseTestCase

from users.models import Profile


# Create your tests here.


class UnContrastSubmittedStudiesViewSetTestCase(UnContrastBaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    # @skip("Not implemented experiments submission yet")
    # def test_study_and_experiment_sub_relations_creation_by_user(self):
    #     """
    #     test study is created with 201
    #     test approval status is pending and approval process is created
    #     test submitter gets study back, but other user don't
    #     """
    #     self.given_user_exists(username="submitting_user")
    #     self.given_user_authenticated("submitting_user", "12345")
    #     study_res = self.when_uncontrast_study_created_by_user_via_api()
    #
    #     res = self.get_pending_studies()
    #     self.assertEqual(len(res["results"]), 1)
    #
    #     first_result = res["results"][0]
    #     res = self.get_specific_study(first_result["id"])
    #     self.assertEqual(res["approval_status"], ApprovalChoices.PENDING)
    #
    #     self.assertIsNotNone(res["approval_process"])
    #     study_id = study_res["id"]
    #     study = Study.objects.get(id=study_id)
    #     self.assertEqual(study.approval_process.started_at.date(), datetime.date.today())
    #
    #     experiments_res = self.get_experiments_for_study(first_result["id"])
    #     self.assertEqual(len(experiments_res), 0)
    #     rpt_theory = Theory.objects.get(name="RPT")
    #     res_experiment = self.when_experiment_is_added_to_study_via_api(study_id=first_result["id"])
    #
    #     self.assertListEqual(res_experiment["techniques"], [])
    #     self.assertListEqual(res_experiment["tasks"], [])
    #
    #     experiments_res = self.get_experiments_for_study(study_id)
    #     self.assertEqual(len(experiments_res), 1)
    #
    #     experiment_id = res_experiment["id"]
    #     parent_paradigm, created = Paradigm.objects.get_or_create(
    #         name="Abnormal Contents of Consciousness", parent=None, sub_type=None
    #     )
    #     paradigm, created = Paradigm.objects.get_or_create(name="Amusia", parent=parent_paradigm, sub_type=None)
    #     technique, created = Technique.objects.get_or_create(name="fMRI")
    #     task_type, created = TaskType.objects.get_or_create(name="Discrimination")
    #     stimulus_category, created = StimulusCategory.objects.get_or_create(name="Animals")
    #     stimulus_modality, created = ModalityType.objects.get_or_create(name="Auditory")
    #
    #     paradigms_res = self.when_paradigm_is_added_to_experiment(study_id, experiment_id, paradigm_id=paradigm.id)
    #     technique_res = self.when_technique_is_added_to_experiment(study_id, experiment_id, technique_id=technique.id)
    #     tasks_res = self.when_task_is_added_to_experiment(
    #         study_id, experiment_id, task_data=dict(type=task_type.id, description="we did this")
    #     )
    #
    #     # check with stimulus without subcategory
    #
    #     stimulus_res = self.when_stimulus_is_added_to_experiment(
    #         study_id, experiment_id, stimulus_data=dict(category=stimulus_category.id, modality=stimulus_modality.id)
    #     )
    #     relevant_theories = Theory.objects.filter(parent__isnull=False)
    #     for theory in relevant_theories:
    #         interpretations_res = self.when_interpretation_is_added_to_experiment(
    #             study_id, experiment_id, interpretation_data=dict(theory=theory.id, type=InterpretationsChoices.PRO)
    #         )
    #     task_id = tasks_res["id"]
    #     experiments_res = self.get_experiments_for_study(study_id)
    #     first_experiment = experiments_res[0]
    #     self.assertEqual(first_experiment["paradigms"][0]["name"], "Amusia")
    #     self.assertEqual(first_experiment["techniques"][0]["name"], "fMRI")
    #     self.assertEqual(first_experiment["tasks"][0]["type"], task_type.id)
    #     self.assertEqual(len(first_experiment["interpretations"]), relevant_theories.count())
    #     self.assertEqual(first_experiment["interpretations"][0]["type"], InterpretationsChoices.PRO)
    #
    #     # Now replace it
    #     interpretations_res = self.when_interpretation_is_added_to_experiment(
    #         study_id,
    #         experiment_id,
    #         interpretation_data=dict(theory=relevant_theories[0].id, type=InterpretationsChoices.CHALLENGES),
    #     )
    #
    #     experiments_res = self.get_experiments_for_study(study_id)
    #     first_experiment = experiments_res[0]
    #     # verify count hasn't been changed
    #     self.assertEqual(len(first_experiment["interpretations"]), relevant_theories.count())
    #     for interpretation in first_experiment["interpretations"]:
    #         if interpretation["theory"] == relevant_theories[0].id:
    #             self.assertEqual(
    #                 first_experiment["interpretations"][0]["type"], InterpretationsChoices.CHALLENGES
    #             )  # data has been updated
    #             break
    #
    #     paradigms_res = self.when_paradigm_is_removed_from_experiment(study_id, experiment_id, paradigm_id=paradigm.id)
    #     technique_res = self.when_technique_is_removed_from_experiment(
    #         study_id, experiment_id, technique_id=technique.id
    #     )
    #     tasks_res = self.when_task_is_removed_from_experiment(study_id, experiment_id, task_id)
    #     experiments_res = self.get_experiments_for_study(study_id)
    #     self.assertListEqual(experiments_res[0]["paradigms"], [])
    #     self.assertListEqual(experiments_res[0]["techniques"], [])
    #     self.assertListEqual(experiments_res[0]["tasks"], [])
    #
    #     # now submit to review
    #     self.when_study_is_submitted_to_review(study_id)

    # @skip("Not implemented experiments submission yet")
    def test_study_and_experiment_deletion_by_user(self):
        """
        test study is created with 201
        test approval status is pending and approval process is created
        test submitter gets study back, but other user don't
        """
        self.given_user_exists(username="submitting_user")
        self.given_user_authenticated("submitting_user", "12345")
        study_res = self.when_uncontrast_study_created_by_user_via_api()

        study_id = study_res["id"]

        experiments_res = self.get_experiments_for_study(study_id)
        self.assertEqual(len(experiments_res), 0)
        main_paradigm = self.given_uncon_main_paradigm_exists("main_paradigm")

        specific_paradigm = self.given_uncon_specific_paradigm_exists("specific_paradigm", main=main_paradigm)

        res_experiment = self.when_experiment_is_added_to_study_via_api(study_id=study_id, paradigm_id=specific_paradigm.id)
        experiment_id = res_experiment["id"]
        experiments_res = self.get_experiments_for_study(study_id)
        self.assertEqual(len(experiments_res), 1)
        self.add_experiment_findings_notes_to_experiment(
            study_id=study_id, experiment_id=experiment_id, notes="the results are here"
        )
        # trying with empty
        self.add_experiment_findings_notes_to_experiment(study_id=study_id, experiment_id=experiment_id, notes="bla notes")
        experiments_res = self.get_experiments_for_study(study_id)
        self.assertEqual(experiments_res[0]["experiment_findings_notes"], "bla notes")
        self.assertEqual(experiments_res[0]["type"], ExperimentTypeChoices.BEHAVIORAL)
        self.add_experiment_findings_notes_to_experiment(study_id=study_id, experiment_id=experiment_id, notes="")
        experiments_res = self.get_experiments_for_study(study_id)
        self.assertEqual(experiments_res[0]["experiment_findings_notes"], "")

        delete_experiment_res = self.when_experiment_is_removed_from_study(study_id, experiment_id)

        experiments_res = self.get_experiments_for_study(study_id)
        self.assertEqual(len(experiments_res), 0)

        delete_study_res = self.when_study_is_removed(study_id)

        studies_res = self.get_pending_studies()
        self.assertEqual(studies_res["count"], 0)

    @skip("Not implemented experiments submission yet")
    def test_study_and_experiment_deletion_by_reviewer_user(self):
        """
        test study is created with 201
        test approval status is pending and approval process is created
        test submitter gets study back, but other user don't
        """
        self.given_user_exists(username="submitting_user")

        registration_res = self.when_user_is_registered(
            username="reviewer_user", password="12345", email="test@email.com"
        )

        reviewer_profile = Profile.objects.get(user__username="reviewer_user")
        # create experiment and study by a regular user
        self.given_user_authenticated("submitting_user", "12345")
        study_res = self.when_uncontrast_study_created_by_user_via_api()

        study_id = study_res["id"]

        experiments_res = self.get_experiments_for_study(study_id)
        self.assertEqual(len(experiments_res), 0)
        res_experiment = self.when_experiment_is_added_to_study_via_api(study_id=study_id)
        experiment_id = res_experiment["id"]

        self.given_user_authenticated("reviewer_user", "12345")

        # verify this would fail with permission error
        self.add_results_summary_to_experiment(
            study_id=study_id,
            experiment_id=experiment_id,
            results_summary="the results are here",
            expected_result_code=status.HTTP_403_FORBIDDEN,
        )

        res = self.when_user_fetches_their_studies()
        self.assertEqual(len(res), 0)

        # Now we move the user to be a reviewer
        reviewer_profile.is_reviewer = True
        reviewer_profile.save()

        # Now should work

        res = self.when_user_fetches_their_studies()
        self.assertEqual(len(res), 1)

        self.add_results_summary_to_experiment(
            study_id=study_id, experiment_id=experiment_id, results_summary="the results are here"
        )
        # trying with empty

        delete_experiment_res = self.when_experiment_is_removed_from_study(study_id, experiment_id)

        experiments_res = self.get_experiments_for_study(study_id)
        self.assertEqual(len(experiments_res), 0)

        delete_study_res = self.when_study_is_removed(study_id)

        studies_res = self.get_pending_studies()
        self.assertEqual(studies_res["count"], 0)

    def test_study_creation_and_update_flow(self):
        """
        test study is created with 201
        test approval status is pending and approval process is created
        test submitter gets study back, but other user don't
        """
        self.given_user_exists(username="submitting_user", email="submitting_user@test.com")
        self.given_user_authenticated("submitting_user", "12345")
        author1 = self.given_an_author_exists("author1")
        study_res = self.when_uncontrast_study_created_by_user_via_api(authors_key_words=[], authors=[author1.id])
        study_id = study_res["id"]
        self.assertEqual(study_res["authors"][0]["name"], author1.name)
        # verify status in "my_studies"

        res = self.when_user_fetches_their_studies()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["approval_status"], ApprovalChoices.PENDING)

        update_res = self.when_study_is_updated(study_id, authors_key_words=["what"], countries=["GB", "IL"])
        self.assertListEqual(update_res["countries"], ["GB", "IL"])
        self.assertEqual(update_res["authors"][0]["name"], author1.name)

        res = self.get_pending_studies()
        self.assertEqual(len(res["results"]), 1)
        self.when_study_is_submitted_to_review(study_id)
        res = self.when_user_fetches_their_studies()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["approval_status"], ApprovalChoices.AWAITING_REVIEW)

    def test_study_submission_behavior(self):
        """
        test study is created with 201
        test approval status is pending and approval process is created
        """
        self.given_user_exists(username="submitting_user", email="submitting_user@test.com")
        self.given_user_authenticated("submitting_user", "12345")
        author1 = self.given_an_author_exists("author1")
        study_res = self.when_uncontrast_study_created_by_user_via_api(authors_key_words=[], authors=[author1.id])
        study_id = study_res["id"]

        # one email for site manager and one for recipient
        self.verify_mailbox_emails_count_by_predicate(
            lambda x: x.subject.lower() == "regarding your submission to uncontrast database", 0
        )
        self.verify_mailbox_emails_count_by_predicate(
            lambda x: x.subject.lower() == "an uncontrast submission was received", 0
        )
        self.when_study_is_submitted_to_review(study_id)
        self.verify_mailbox_emails_count_by_predicate(
            lambda x: x.subject.lower() == "regarding your submission to uncontrast database", 1
        )
        self.verify_mailbox_emails_count_by_predicate(
            lambda x: x.subject.lower() == "uncontrast submission was received", 1
        )

    def test_study_approve_reject_flow(self):
        self.given_user_exists(username="submitting_user", email="submitting_user@test.com")
        self.given_user_authenticated("submitting_user", "12345")
        author1 = self.given_an_author_exists("author1")
        study_res = self.when_uncontrast_study_created_by_user_via_api(authors_key_words=[], authors=[author1.id])
        study_id = study_res["id"]

        self.when_study_is_submitted_to_review(study_id)

        self.given_user_exists(username="admin_user", is_staff=True, is_superuser=True)
        self.given_admin_user_authenticated("admin_user", "12345")
        self.when_admin_approves_study(study_id)

        self.verify_mailbox_emails_count_by_predicate(
            lambda x: x.subject.lower() == "regarding your submission to uncontrast database"
            and "We are glad to notify you that following review by a member" in x.body,
            1,
        )
        study = Study.objects.get(id=study_id)
        self.assertEqual(study.approval_status, ApprovalChoices.APPROVED)
        self.assertEqual(study.approval_process.comments.last().text, "Submission approved")

        self.when_admin_rejects_study(study_id)

        self.verify_mailbox_emails_count_by_predicate(
            lambda x: x.subject.lower() == "regarding your submission to uncontrast database"
            and "decided that it is outside the scope of our database" in x.body,
            1,
        )
        study = Study.objects.get(id=study_id)
        self.assertEqual(study.approval_status, ApprovalChoices.REJECTED)
        self.assertEqual(study.approval_process.comments.last().text, "Submission rejected")
        self.assertEqual(len(study.approval_process.comments.all()), 2)

    def when_uncontrast_study_created_by_user_via_api(self, **kwargs):
        default_study = dict(
            DOI="10.1016/j.cortex.2017.07.010",
            title="a study",
            year=1990,
            corresponding_author_email="test@example.com",
            authors=[],
            authors_key_words=["key", "word"],
            affiliations="some affiliations",
            countries=["IL"],
        )
        study_params = {**default_study, **kwargs}

        target_url = reverse("uncontrast-studies-submitted-list")
        res = self.client.post(target_url, data=json.dumps(study_params), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def when_experiment_is_added_to_study_via_api(self, study_id: int, paradigm_id:int, **kwargs):
        target_url = reverse("uncontrast-studies-experiments-list", args=[study_id])
        default_experiment = dict(
            paradigm=paradigm_id,
            is_target_stimulus=True,
            is_target_same_as_suppressed_stimulus=True,
            # type=ExperimentTypeChoices.BEHAVIORAL,
            consciousness_measures_notes="consciousness_measures_notes",
            experiment_findings_notes="experiment_findings_notes",
        )
        experiment_params = {**default_experiment, **kwargs}
        res = self.client.post(target_url, data=json.dumps(experiment_params), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def get_pending_studies(self):
        target_url = reverse("uncontrast-studies-submitted-list")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data

    def get_specific_study(self, study_id):
        target_url = reverse("uncontrast-studies-submitted-detail", args=[study_id])
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data

    def get_experiments_for_study(self, study_id):
        target_url = reverse("uncontrast-studies-experiments-list", args=[study_id])
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data

    def when_study_is_updated(self, study_id, **kwargs):
        target_url = reverse("uncontrast-studies-submitted-detail", args=[study_id])
        res = self.client.patch(target_url, data=json.dumps(kwargs), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data

    def when_task_is_added_to_experiment(self, study_id, experiment_id, task_data):
        target_url = reverse("uncontrast-tasks-list", args=[study_id, experiment_id])
        res = self.client.post(target_url, data=json.dumps(task_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def when_suppressed_stimulus_is_added_to_experiment(self, study_id, experiment_id, stimulus_data):
        target_url = reverse("uncontrast-suppressed-stimuli-list", args=[study_id, experiment_id])
        res = self.client.post(target_url, data=json.dumps(stimulus_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def when_target_stimulus_is_added_to_experiment(self, study_id, experiment_id, stimulus_data):
        target_url = reverse("uncontrast-target-stimuli-list", args=[study_id, experiment_id])
        res = self.client.post(target_url, data=json.dumps(stimulus_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def when_experiment_is_removed_from_study(self, study_id: int, experiment_id: int):
        target_url = reverse("uncontrast-studies-experiments-detail", args=[study_id, experiment_id])
        res = self.client.delete(target_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        return res.data

    def when_study_is_removed(self, study_id: int):
        target_url = reverse("uncontrast-studies-submitted-detail", args=[study_id])
        res = self.client.delete(target_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        return res.data

    def when_task_is_removed_from_experiment(self, study_id, experiment_id, task_id):
        target_url = reverse("uncontrast-tasks-detail", args=[study_id, experiment_id, task_id])
        res = self.client.delete(target_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        return res.data

    def when_study_is_submitted_to_review(self, study_id):
        target_url = reverse("uncontrast-studies-submitted-submit-to-review", args=[study_id])
        res = self.client.post(target_url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def when_user_fetches_their_studies(self):
        target_url = reverse("uncontrast-studies-submitted-my-studies")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data

    def add_experiment_findings_notes_to_experiment(
        self, study_id: int, experiment_id: int, notes, expected_result_code=status.HTTP_201_CREATED
    ):
        target_url = reverse("uncontrast-studies-experiments-set-experiment-findings-notes", args=[study_id, experiment_id])
        res = self.client.post(target_url, json.dumps(dict(note=notes)), content_type="application/json")
        self.assertEqual(res.status_code, expected_result_code)

    def add_experiment_consciousness_measures_notes_to_experiment(
        self, study_id: int, experiment_id: int, notes, expected_result_code=status.HTTP_201_CREATED
    ):
        target_url = reverse("uncontrast-studies-experiments-set-consciousness-measures-notes", args=[study_id, experiment_id])
        res = self.client.post(target_url, json.dumps(dict(note=notes)), content_type="application/json")
        self.assertEqual(res.status_code, expected_result_code)
