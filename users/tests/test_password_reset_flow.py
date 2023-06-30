from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status

from contrast_api.tests.base import BaseTestCase
import urllib.parse


class UserPasswordResetTestCase(BaseTestCase):
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
