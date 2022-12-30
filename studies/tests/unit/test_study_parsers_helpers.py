from unittest import TestCase

from studies.studies_parsing_helpers import parse_authors_from_affiliation_text, resolve_country_from_affiliation_text


class StudyParserHelpersTestCase(TestCase):
    def test_parsing_authors_from_affiliation_text(self):
        text = ''
        res = parse_authors_from_affiliation_text(text)
        pass

    def test_resolving_countries_from_affiliation_text(self):
        text = ''
        res = resolve_country_from_affiliation_text(text)
        pass