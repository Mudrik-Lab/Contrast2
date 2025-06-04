from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

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

    def test_study_admin_changelist_loads(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("admin:studies_study_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
