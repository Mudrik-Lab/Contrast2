from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# Create your tests here.
class ExperimentsViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_experiments_endpoint_is_responding_to_list(self):
        target_url = reverse("experiments-list")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_nations_of_consciousness_data(self):
        """
        provide graph_type=nations_of_consciousness, min_experiments?=int
        returns experiments grouped by country and interpretations (positive to theory)
        """
        pass

    def test_publications_by_theory_family_data(self):
        """
        provide graph_type=publications_by_theory, min_experiments?=int, theory=GNW
        group by publications names
        """
        pass

    def test_frequencies_graph(self):
        pass


    def test_timings_graphs(self):
        pass

    def test_theory_driven_by_interpretations(self):
        """
        is_reporting[]=true, TypeOfConsciousness[]=state
        hint: use request.query_params.getlist
        """
        pass
