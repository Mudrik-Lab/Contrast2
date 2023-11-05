from django.urls import reverse

from contrast_api.tests.base import BaseTestCase
from studies.models import Author


class AuthorsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_get_existing_authors(self):
        self.given_user_exists(username="submitting_user")

        self.given_user_authenticated("submitting_user", "12345")

        self.given_an_author_exists("special author")

        res = self.when_a_user_searches_for_author("bla")
        self.assertEqual(len(res.data["results"]), 0)

        res = self.when_a_user_searches_for_author("spec")
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["name"], "special author")

    def test_adding_an_author_flow_including_search(self):
        self.given_user_exists(username="submitting_user")

        self.given_user_authenticated("submitting_user", "12345")
        res = self.when_a_user_searches_for_author("bla")
        self.assertEqual(len(res.data["results"]), 0)

        self.when_a_user_creates_an_auther("mr researcher")

        res = self.when_a_user_searches_for_author("cher")
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["name"], "mr researcher")
