from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class AdminViewsTest(TestCase):
    def setUp(self):
        self.username = "testadmin_uncontrast"
        self.password = "testpassword_uncontrast"
        self.admin_user = User.objects.create_superuser(
            username=self.username,
            password=self.password,
            email="testadmin_uncontrast@example.com"
        )

    def test_uncon_experiment_admin_changelist_loads(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("admin:uncontrast_studies_unconexperiment_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_uncon_consciousness_measure_admin_changelist_loads(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("admin:uncontrast_studies_unconsciousnessmeasure_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_uncon_sample_admin_changelist_loads(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("admin:uncontrast_studies_unconsample_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_uncon_target_stimulus_admin_changelist_loads(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("admin:uncontrast_studies_uncontargetstimulus_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
