from typing import Dict

from django.conf import settings
from django.urls import reverse
from rest_framework import status

from contrast_api.tests.base import BaseTestCase


class UserFeedbackTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_user_feedback(self):
        email = "user1@test.com"

        self.verify_no_email_was_sent_to_user(email=settings.SITE_MANAGER_ADDRESS)
        feedback_type = "site-feedback"
        feedback_data = dict(queries_score=4, experience_score=3, completeness_score=5, paper_uploading_score=4,
                             comments="comments are here")
        res = self.when_user_provides_feedback(email=email, feedback_type=feedback_type, feedback_data=feedback_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.verify_email_was_sent_to_user(email=settings.SITE_MANAGER_ADDRESS)

    def test_contact_form_with_confirm_updates_false(self):
        email = "user1@test.com"

        self.verify_no_email_was_sent_to_user(email=settings.SITE_MANAGER_ADDRESS)
        feedback_type = "contact-us"
        feedback_data = dict(subject="my contact", message="what ever")
        res = self.when_user_provides_feedback(email=email, feedback_type=feedback_type, feedback_data=feedback_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.verify_email_was_sent_to_user(email=settings.SITE_MANAGER_ADDRESS)

    def when_user_provides_feedback(self, email: str, feedback_type: str, feedback_data: Dict):
        url = reverse(f"feedback-{feedback_type}")
        data = dict(email=email, **feedback_data)
        res = self.client.post(url, data=data)
        return res
