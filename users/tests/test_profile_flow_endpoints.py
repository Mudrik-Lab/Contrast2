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

    def test_user_registration_case(self):
        user_birthdate = (timezone.now() - datetime.timedelta(days=365 * 30)).strftime("%Y-%m-%d")
        username = "user1"
        password = "12345"

        res = self.when_user_logs_in(username, password)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.when_user_is_registered(email="user1@test.com",
                                           username=username,
                                           password=password,
                                           date_of_birth=user_birthdate,
                                           academic_stage=AcademicStageChoices.UNDERGRADUATE,
                                           self_identified_gender=GenderChoices.NOT_REPORTING)

        login_res = self.when_user_logs_in(username, password)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.given_user_authenticated(login_res)
        home_res = self.when_user_access_home()
        self.assertEqual(home_res.status_code, status.HTTP_200_OK)
        self.assertEqual(home_res.data.get("academic_stage"), AcademicStageChoices.UNDERGRADUATE)

    def when_user_is_registered(self, email, password, **kwargs):
        data = dict(email=email, password=password, **kwargs)
        res = self.client.post(reverse("profiles-register"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res.data

    def given_user_authenticated(self, res):
        access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def when_user_logs_in(self, username, password):
        auth_url = reverse("api-token-obtain-pair")
        res = self.client.post(auth_url, data=dict(username=username, password=password))
        return res

    def when_user_access_home(self):
        res = self.client.get(reverse("profiles-home"))
        return res
