import datetime
import json

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from contrast_api.tests.base import BaseTestCase
from users.choices import GenderChoices, AcademicStageChoices


class UserRegistrationTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_user_registration_without_actually_creating_a_profile_first(self):
        (timezone.now() - datetime.timedelta(days=365 * 30)).strftime("%Y-%m-%d")
        username = "user1"
        password = "12345"
        email = "user1@test.com"

        self.when_user_is_registered(username=username, password=password, email=email)

        # Should allow logging in
        login_res = self.when_user_logs_in(username, password)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.given_user_authenticated_with_access_token(login_res)

        # Expected not to fail and exist
        home_res = self.when_user_access_home()
        self.assertEqual(home_res.status_code, status.HTTP_200_OK)
        self.assertIsNone(home_res.data.get("academic_stage"))

        # Now update the academic stage

        self.when_user_updates_data(
            profile_id=home_res.data["id"], academic_stage=AcademicStageChoices.POSTDOC, email="my_new_email@test.com"
        )

        # verify the change
        home_res = self.when_user_access_home()
        self.assertEqual(home_res.status_code, status.HTTP_200_OK)
        self.assertEqual(home_res.data.get("academic_stage"), AcademicStageChoices.POSTDOC)
        self.assertEqual("my_new_email@test.com", home_res.data.get("email"))

    def test_user_registration_case(self):
        user_birthdate = (timezone.now() - datetime.timedelta(days=365 * 30)).strftime("%Y-%m-%d")
        username = "user1"
        password = "12345"
        email = "user1@test.com"

        res = self.when_user_logs_in(username, password)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Should not show the username exists
        res = self.when_user_does_username_check(username)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["exists"])

        res = self.when_user_is_registered(username=username, password=password, email=email)

        # Should allow logging in
        login_res = self.when_user_logs_in(username, password)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.given_user_authenticated_with_access_token(login_res)

        res = self.when_user_profile_is_registered(
            date_of_birth=user_birthdate,
            academic_stage=AcademicStageChoices.UNDERGRADUATE,
            self_identified_gender=GenderChoices.NOT_REPORTING,
        )

        # Should now show the username does exists
        res = self.when_user_does_username_check(username)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["exists"])

        # Supports home endpoint
        home_res = self.when_user_access_home()
        self.assertEqual(home_res.status_code, status.HTTP_200_OK)
        self.assertEqual(home_res.data.get("academic_stage"), AcademicStageChoices.UNDERGRADUATE)

    def test_user_update_case(self):
        user_birthdate = (timezone.now() - datetime.timedelta(days=365 * 30)).strftime("%Y-%m-%d")
        username = "user1"
        password = "12345"
        email = "user1@test.com"

        self.when_user_is_registered(username=username, password=password, email=email)

        # Should allow logging in
        login_res = self.when_user_logs_in(username, password)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.given_user_authenticated_with_access_token(login_res)

        self.when_user_profile_is_registered(
            date_of_birth=user_birthdate,
            academic_stage=AcademicStageChoices.UNDERGRADUATE,
            self_identified_gender=GenderChoices.NOT_REPORTING,
        )

        # Supports home endpoint
        home_res = self.when_user_access_home()
        self.assertEqual(home_res.status_code, status.HTTP_200_OK)
        self.assertEqual(home_res.data.get("academic_stage"), AcademicStageChoices.UNDERGRADUATE)

        # Now update the academic stage

        self.when_user_updates_data(
            profile_id=home_res.data["id"], academic_stage=AcademicStageChoices.POSTDOC, email="my_new_email@test.com"
        )

        # verify the change
        home_res = self.when_user_access_home()
        self.assertEqual(home_res.status_code, status.HTTP_200_OK)
        self.assertEqual(home_res.data.get("academic_stage"), AcademicStageChoices.POSTDOC)
        self.assertEqual("my_new_email@test.com", home_res.data.get("email"))

    def when_user_profile_is_registered(self, **kwargs):
        data = dict(**kwargs)
        res = self.client.post(reverse("profiles-register"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def when_user_updates_data(self, profile_id, **kwargs):
        res = self.client.patch(
            reverse("profiles-detail", args=[profile_id]),
            data=json.dumps(dict(**kwargs)),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data

    def given_user_authenticated_with_access_token(self, res):
        access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
