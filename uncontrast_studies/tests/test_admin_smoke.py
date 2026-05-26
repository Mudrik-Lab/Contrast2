from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

APP_LABEL = "uncontrast_studies"


class AdminChangelistSmokeTest(TestCase):
    """
    Smokes every admin-registered model's changelist in the uncontrast_studies app.
    Guards against breakage from Django / library upgrades without depending
    on per-model fixtures — empty changelists still exercise list_display,
    list_filter, search_fields, and queryset overrides.
    """

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            username="admin_smoke_uncontrast", password="x", email="admin_smoke_uncontrast@example.com"
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_all_registered_changelists_load(self):
        models = [m for m in admin.site._registry if m._meta.app_label == APP_LABEL]
        self.assertGreater(len(models), 0, f"No admin models registered for app '{APP_LABEL}'")

        for model in models:
            with self.subTest(model=model.__name__):
                url = reverse(f"admin:{APP_LABEL}_{model._meta.model_name}_changelist")
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    200,
                    f"{model.__name__} changelist returned {response.status_code}",
                )
