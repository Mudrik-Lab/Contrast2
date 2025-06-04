from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from studies.models import Study, Experiment
from approval_process.choices import ApprovalChoices
from contrast_api.choices import (
    TheoryDrivenChoices,
    TypeOfConsciousnessChoices,
    ReportingChoices,
    ExperimentTypeChoices,
    DirectionChoices,            # Added
)
from studies.models import FindingTag, FindingTagFamily, FindingTagType, Technique # Added
from django_countries import countries

User = get_user_model()

class AdminViewsTest(TestCase):
    def setUp(self):
        self.username = "testadmin"
        self.password = "testpassword"
        self.admin_user = User.objects.create_superuser(
            username=self.username,
            password=self.password,
            email="testadmin@example.com"
        )
        self.client.login(username=self.username, password=self.password)

        # Create some Study objects for filter testing and store them on self
        self.study_pending = Study.objects.create(
            title="Study Pending",
            DOI="10.123/pending", # Changed DOI to match later test usage
            approval_status=ApprovalChoices.PENDING,
            year=2020,
            countries=["US"], # Corrected: Must be a list/tuple for multiple=True
            type="ORIGINAL", # Added based on later prompt examples
            is_author_submitter=True, # Added based on later prompt examples
            submitter=self.admin_user,
            abbreviated_source_title="Journal X"
        )
        self.study_approved = Study.objects.create(
            title="Study Approved",
            DOI="10.123/approved", # Changed DOI to match later test usage
            approval_status=ApprovalChoices.APPROVED,
            year=2021,
            countries=["CA"], # Corrected: Must be a list/tuple for multiple=True
            type="REPLICATION", # Added based on later prompt examples
            is_author_submitter=False, # Added based on later prompt examples
            submitter=self.admin_user,
            abbreviated_source_title="Journal Y"
        )
        self.study_rejected = Study.objects.create(
            title="Study Rejected",
            DOI="10.123/rejected", # Changed DOI to match later test usage
            approval_status=ApprovalChoices.REJECTED,
            year=2020,
            countries=["US"], # Corrected: Must be a list/tuple for multiple=True
            type="META_ANALYSIS", # Added based on later prompt examples
            submitter=self.admin_user, # Added based on later prompt examples
            abbreviated_source_title="Journal X" # Added based on later prompt examples
        )

    def test_study_admin_changelist_loads(self):
        # self.client.login(username=self.username, password=self.password) # Moved to setUp
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_experiment_admin_changelist_loads(self):
        # self.client.login(username=self.username, password=self.password) # Moved to setUp
        url = reverse("admin:studies_experiment_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_author_admin_changelist_loads(self):
        # self.client.login(username=self.username, password=self.password) # Moved to setUp
        url = reverse("admin:studies_author_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_findingtag_admin_changelist_loads(self):
        # self.client.login(username=self.username, password=self.password) # Moved to setUp
        url = reverse("admin:studies_findingtag_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_theory_admin_changelist_loads(self):
        # self.client.login(username=self.username, password=self.password) # Moved to setUp
        url = reverse("admin:studies_theory_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_study_admin_filter_by_approval_status(self):
        url = reverse("admin:studies_study_changelist")
        # Test with PENDING
        response = self.client.get(url, {"approval_status": ApprovalChoices.PENDING}) # Corrected
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Pending")
        self.assertNotContains(response, "Study Approved")

        # Test with APPROVED
        response = self.client.get(url, {"approval_status": ApprovalChoices.APPROVED})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Approved")
        self.assertNotContains(response, "Study Pending")

    def test_study_admin_filter_by_country(self):
        url = reverse("admin:studies_study_changelist")
        # Test with US
        response = self.client.get(url, {"country": "US"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Pending")
        self.assertContains(response, "Study Rejected")
        self.assertNotContains(response, "Study Approved")

        # Test with CA
        response = self.client.get(url, {"country": "CA"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Approved")
        self.assertNotContains(response, "Study Pending")

    def test_study_admin_filter_by_year(self):
        url = reverse("admin:studies_study_changelist")
        # Test with year 2020
        response = self.client.get(url, {"year__gte": "2020", "year__lte": "2020"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Pending")
        self.assertContains(response, "Study Rejected")
        self.assertNotContains(response, "Study Approved")

        # Test with year 2021
        response = self.client.get(url, {"year__gte": "2021", "year__lte": "2021"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Approved")
        self.assertNotContains(response, "Study Pending")

    # More detailed filter tests based on the second part of the prompt
    def test_study_admin_filter_by_approval_status_approved_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"approval_status__exact": ApprovalChoices.APPROVED})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Study Approved") # Adjusted title to match setUp

    def test_study_admin_filter_by_approval_status_pending_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"approval_status__exact": ApprovalChoices.PENDING}) # Corrected
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Study Pending") # Adjusted title

    def test_study_admin_filter_by_approval_status_rejected_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"approval_status__exact": ApprovalChoices.REJECTED})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Study Rejected") # Adjusted title

    def test_study_admin_filter_by_type_original_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"type__exact": "ORIGINAL"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Study Pending") # Original type was "Study Pending"

    def test_study_admin_filter_by_is_author_submitter_true_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"is_author_submitter__exact": "1"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Study Pending") # is_author_submitter=True was "Study Pending"

    def test_study_admin_filter_by_is_author_submitter_false_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"is_author_submitter__exact": "0"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Study Approved") # is_author_submitter=False was "Study Approved"

    def test_study_admin_filter_by_year_range_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"year__gte": "2020", "year__lte": "2020"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 2) # Study Pending and Study Rejected are year 2020
        self.assertTrue(all(s.year == 2020 for s in queryset))

        response = self.client.get(url, {"year__gte": "2021", "year__lte": "2021"}) # Corrected range
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(all(s.year == 2021 for s in queryset))
        self.assertEqual(queryset.first().title, "Study Approved")

    def test_study_admin_filter_by_country_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"country": "US"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 2) # Study Pending and Study Rejected are US
        for study in queryset:
            self.assertTrue(any(country_code == "US" for country_code in study.countries)) # Assuming list of strings

        response = self.client.get(url, {"country": "CA"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertTrue(any(country_code == "CA" for country_code in queryset.first().countries)) # Assuming list of strings
        self.assertEqual(queryset.first().title, "Study Approved")

    def test_study_admin_filter_by_journal_detailed(self):
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url, {"journal": "Journal X"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 2)
        self.assertTrue(all(s.abbreviated_source_title == "Journal X" for s in queryset))

        response = self.client.get(url, {"journal": "Journal Y"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().abbreviated_source_title, "Journal Y")
        self.assertEqual(queryset.first().title, "Study Approved")

    def test_experiment_admin_filter_by_type_of_consciousness(self):
        # self.client.login(username=self.username, password=self.password) # Already logged in from setUp
        exp1 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
            type=ExperimentTypeChoices.BEHAVIORAL,
            is_reporting=ReportingChoices.REPORT,
            theory_driven=TheoryDrivenChoices.DRIVEN
        )
        exp2 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.STATE,
            type=ExperimentTypeChoices.NEUROSCIENTIFIC, # Assuming EEG is Neuroscientific
            is_reporting=ReportingChoices.NO_REPORT,
            theory_driven=TheoryDrivenChoices.POST_HOC
        )

        url = reverse("admin:studies_experiment_changelist")
        response = self.client.get(url, {"type_of_consciousness__exact": TypeOfConsciousnessChoices.CONTENT.value})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().type_of_consciousness, TypeOfConsciousnessChoices.CONTENT)

        exp1.delete()
        exp2.delete()

    def test_findingtag_admin_filter_by_direction(self):
        # self.client.login(username=self.username, password=self.password) # Already logged in
        exp = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
            type=ExperimentTypeChoices.BEHAVIORAL,
            is_reporting=ReportingChoices.REPORT,
            theory_driven=TheoryDrivenChoices.DRIVEN
        )
        default_family = FindingTagFamily.objects.create(name="Temporal") # Requires onset & offset
        default_type = FindingTagType.objects.create(name="DefaultType", family=default_family)

        ft1 = FindingTag.objects.create(experiment=exp, family=default_family, type=default_type, direction=DirectionChoices.POSITIVE, is_NCC=True, onset=10, offset=20)
        ft2 = FindingTag.objects.create(experiment=exp, family=default_family, type=default_type, direction=DirectionChoices.NEGATIVE, is_NCC=False, onset=30, offset=40)

        url = reverse("admin:studies_findingtag_changelist")
        response = self.client.get(url, {"direction__exact": DirectionChoices.POSITIVE.value})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().direction, DirectionChoices.POSITIVE)

        ft1.delete()
        ft2.delete()
        default_type.delete()
        default_family.delete()
        exp.delete()

    def test_findingtag_admin_filter_by_is_ncc(self):
        # self.client.login(username=self.username, password=self.password)
        exp = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
            type=ExperimentTypeChoices.BEHAVIORAL,
            is_reporting=ReportingChoices.REPORT,
            theory_driven=TheoryDrivenChoices.DRIVEN
        )
        default_family = FindingTagFamily.objects.create(name="Temporal") # Requires onset & offset
        default_type = FindingTagType.objects.create(name="DefaultType", family=default_family)

        ft1 = FindingTag.objects.create(experiment=exp, family=default_family, type=default_type, direction=DirectionChoices.POSITIVE, is_NCC=True, onset=10, offset=20)
        ft2 = FindingTag.objects.create(experiment=exp, family=default_family, type=default_type, direction=DirectionChoices.NEGATIVE, is_NCC=False, onset=30, offset=40)

        url = reverse("admin:studies_findingtag_changelist")
        # Filter for is_NCC = True
        response_true = self.client.get(url, {"is_NCC__exact": "1"})
        self.assertEqual(response_true.status_code, 200)
        queryset_true = response_true.context["cl"].queryset
        self.assertEqual(queryset_true.count(), 1)
        self.assertTrue(queryset_true.first().is_NCC)

        # Filter for is_NCC = False
        response_false = self.client.get(url, {"is_NCC__exact": "0"})
        self.assertEqual(response_false.status_code, 200)
        queryset_false = response_false.context["cl"].queryset
        self.assertEqual(queryset_false.count(), 1)
        self.assertFalse(queryset_false.first().is_NCC)

        ft1.delete()
        ft2.delete()
        default_type.delete()
        default_family.delete()
        exp.delete()

    def test_findingtag_admin_filter_by_family(self):
        # self.client.login(username=self.username, password=self.password)
        exp = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
            type=ExperimentTypeChoices.BEHAVIORAL,
            is_reporting=ReportingChoices.REPORT,
            theory_driven=TheoryDrivenChoices.DRIVEN
        )

        family1 = FindingTagFamily.objects.create(name="Temporal") # Using "Temporal" to satisfy onset/offset
        type1 = FindingTagType.objects.create(name="TypeAlpha", family=family1)
        family2 = FindingTagFamily.objects.create(name="OtherFamily") # Not "Temporal"
        type2 = FindingTagType.objects.create(name="TypeBeta", family=family2)

        ft1 = FindingTag.objects.create(experiment=exp, family=family1, type=type1, direction=DirectionChoices.POSITIVE, onset=10, offset=20) # Added offset
        ft2 = FindingTag.objects.create(experiment=exp, family=family2, type=type2, direction=DirectionChoices.POSITIVE) # No onset/offset needed for "OtherFamily"

        url = reverse("admin:studies_findingtag_changelist")
        response = self.client.get(url, {"family__id__exact": family1.id})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().family, family1)

        ft1.delete()
        ft2.delete()
        type1.delete()
        type2.delete()
        family1.delete()
        family2.delete()
        exp.delete()

    def test_findingtag_admin_filter_by_onset_range(self):
        # self.client.login(username=self.username, password=self.password)
        exp = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
            type=ExperimentTypeChoices.BEHAVIORAL,
            is_reporting=ReportingChoices.REPORT,
            theory_driven=TheoryDrivenChoices.DRIVEN
        )
        default_family = FindingTagFamily.objects.create(name="Temporal") # Requires onset & offset
        default_type = FindingTagType.objects.create(name="DefaultType", family=default_family)

        ft1 = FindingTag.objects.create(experiment=exp, family=default_family, type=default_type, onset=100, offset=110, direction=DirectionChoices.POSITIVE)
        ft2 = FindingTag.objects.create(experiment=exp, family=default_family, type=default_type, onset=150, offset=160, direction=DirectionChoices.POSITIVE)
        ft3 = FindingTag.objects.create(experiment=exp, family=default_family, type=default_type, onset=200, offset=210, direction=DirectionChoices.POSITIVE)

        url = reverse("admin:studies_findingtag_changelist")
        # Filter for onset between 140 and 210
        response = self.client.get(url, {"onset__gte": "140", "onset__lte": "210"})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 2)
        self.assertIn(ft2, queryset)
        self.assertIn(ft3, queryset)

        ft1.delete()
        ft2.delete()
        ft3.delete()
        default_type.delete()
        default_family.delete()
        exp.delete()

    def test_experiment_admin_filter_by_type(self):
        exp1 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
            type=ExperimentTypeChoices.BEHAVIORAL,
            is_reporting=ReportingChoices.REPORT,
            theory_driven=TheoryDrivenChoices.DRIVEN
        )
        exp2 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.STATE,
            type=ExperimentTypeChoices.NEUROSCIENTIFIC, # Assuming EEG is Neuroscientific
            is_reporting=ReportingChoices.NO_REPORT,
            theory_driven=TheoryDrivenChoices.POST_HOC
        )

        url = reverse("admin:studies_experiment_changelist")
        response = self.client.get(url, {"type__exact": ExperimentTypeChoices.NEUROSCIENTIFIC.value})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().type, ExperimentTypeChoices.NEUROSCIENTIFIC)

        exp1.delete()
        exp2.delete()

    def test_experiment_admin_filter_by_is_reporting(self):
        exp1 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
            type=ExperimentTypeChoices.BEHAVIORAL,
            is_reporting=ReportingChoices.REPORT,
            theory_driven=TheoryDrivenChoices.DRIVEN
        )
        exp2 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.STATE,
            type=ExperimentTypeChoices.NEUROSCIENTIFIC,
            is_reporting=ReportingChoices.NO_REPORT,
            theory_driven=TheoryDrivenChoices.POST_HOC
        )

        url = reverse("admin:studies_experiment_changelist")
        response_true = self.client.get(url, {"is_reporting__exact": ReportingChoices.REPORT.value})
        self.assertEqual(response_true.status_code, 200)
        queryset_true = response_true.context["cl"].queryset
        self.assertEqual(queryset_true.count(), 1)
        self.assertEqual(queryset_true.first().is_reporting, ReportingChoices.REPORT)

        response_false = self.client.get(url, {"is_reporting__exact": ReportingChoices.NO_REPORT.value})
        self.assertEqual(response_false.status_code, 200)
        queryset_false = response_false.context["cl"].queryset
        self.assertEqual(queryset_false.count(), 1)
        self.assertEqual(queryset_false.first().is_reporting, ReportingChoices.NO_REPORT)

        exp1.delete()
        exp2.delete()

    def test_experiment_admin_filter_by_theory_driven(self):
        exp1 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.CONTENT,
            type=ExperimentTypeChoices.BEHAVIORAL,
            is_reporting=ReportingChoices.REPORT,
            theory_driven=TheoryDrivenChoices.DRIVEN
        )
        exp2 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.STATE,
            type=ExperimentTypeChoices.NEUROSCIENTIFIC,
            is_reporting=ReportingChoices.NO_REPORT,
            theory_driven=TheoryDrivenChoices.POST_HOC
        )

        url = reverse("admin:studies_experiment_changelist")
        response = self.client.get(url, {"theory_driven__exact": TheoryDrivenChoices.DRIVEN.value})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().theory_driven, TheoryDrivenChoices.DRIVEN)

        exp1.delete()
        exp2.delete()

    def test_experiment_admin_filter_by_study_approval_status(self):
        exp1 = Experiment.objects.create(
            study=self.study_approved,
            type_of_consciousness=TypeOfConsciousnessChoices.BOTH, # Was "NA"
            type=ExperimentTypeChoices.BOTH, # Was "OTHER"
            is_reporting=ReportingChoices.REPORT, # Was True
            theory_driven=TheoryDrivenChoices.DRIVEN
        )
        exp2 = Experiment.objects.create(
            study=self.study_pending,
            type_of_consciousness=TypeOfConsciousnessChoices.BOTH, # Was "NA"
            type=ExperimentTypeChoices.BOTH, # Was "OTHER"
            is_reporting=ReportingChoices.REPORT, # Was True
            theory_driven=TheoryDrivenChoices.DRIVEN
        )

        url = reverse("admin:studies_experiment_changelist")
        response = self.client.get(url, {"study__approval_status__exact": ApprovalChoices.APPROVED.value})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["cl"].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().study.approval_status, ApprovalChoices.APPROVED)
        self.assertEqual(queryset.first().study, self.study_approved)

        exp1.delete()
        exp2.delete()
