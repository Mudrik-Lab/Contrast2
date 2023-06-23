import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from contrast_api.tests.base import BaseTestCase
from users.choices import GenderChoices, AcademicStageChoices
import urllib.parse

class UserRegistrationTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_user_reset_password_flow(self):
        username = "user1"
        password = "12345"
        email = "user1@test.com"

        registration_res = self.when_user_is_registered(username=username, password=password, email=email)

        self.verify_no_email_was_sent_to_user(email=email)
        
        res = self.when_user_requests_password_reset(email=email)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        self.verify_email_was_sent_to_user(email=email)
        user = get_user_model().objects.get(id=registration_res["id"])
        token = urllib.parse.quote_plus(PasswordResetTokenGenerator().make_token(user))

        res = self.when_user_resets_password(token=token, password="new_password", email=email)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # verify it fails with old password
        login_res = self.when_user_logs_in(username, password)
        self.assertEqual(login_res.status_code, status.HTTP_401_UNAUTHORIZED)

        # verify it succeeds with new password
        login_res = self.when_user_logs_in(username, "new_password")
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

        
    def test_user_registration_without_actually_creating_a_profile_first(self):
        user_birthdate = (timezone.now() - datetime.timedelta(days=365 * 30)).strftime("%Y-%m-%d")
        username = "user1"
        password = "12345"
        email = "user1@test.com"

        res = self.when_user_is_registered(username=username, password=password, email=email)

        # Should allow logging in
        login_res = self.when_user_logs_in(username, password)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.given_user_authenticated_with_access_token(login_res)

        # Expected not to fail and exist
        home_res = self.when_user_access_home()
        self.assertEqual(home_res.status_code, status.HTTP_200_OK)
        self.assertIsNone(home_res.data.get("academic_stage"))

        # Now update the academic stage

        res = self.when_user_updates_data(profile_id=home_res.data["id"], academic_stage=AcademicStageChoices.POSTDOC,
                                          email="my_new_email@test.com")

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
            self_identified_gender=GenderChoices.NOT_REPORTING)

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

        res = self.when_user_is_registered(username=username, password=password, email=email)

        # Should allow logging in
        login_res = self.when_user_logs_in(username, password)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.given_user_authenticated_with_access_token(login_res)

        res = self.when_user_profile_is_registered(
            date_of_birth=user_birthdate,
            academic_stage=AcademicStageChoices.UNDERGRADUATE,
            self_identified_gender=GenderChoices.NOT_REPORTING)

        # Supports home endpoint
        home_res = self.when_user_access_home()
        self.assertEqual(home_res.status_code, status.HTTP_200_OK)
        self.assertEqual(home_res.data.get("academic_stage"), AcademicStageChoices.UNDERGRADUATE)

        # Now update the academic stage

        res = self.when_user_updates_data(profile_id=home_res.data["id"], academic_stage=AcademicStageChoices.POSTDOC,
                                          email="my_new_email@test.com")

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

    def when_user_is_registered(self, **kwargs):
        data = dict(**kwargs)
        res = self.client.post(reverse("profiles-register-user"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def when_user_updates_data(self, profile_id, **kwargs):
        res = self.client.patch(reverse("profiles-detail", args=[profile_id]), data=json.dumps(dict(**kwargs)),
                                content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data

    def given_user_authenticated_with_access_token(self, res):
        access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

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

    def verify_no_email_was_sent_to_user(self, email:str):
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
