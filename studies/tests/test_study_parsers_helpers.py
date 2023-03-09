from unittest import TestCase

from studies.parsers.historic_data_helpers import find_in_list
from studies.parsers.studies_parsing_helpers import parse_authors_from_authors_text, \
    resolve_country_from_affiliation_text
from studies.tests.base import BaseTestCase


class StudyParserHelpersTestCase(BaseTestCase):
    def test_parsing_authors_from_affiliation_text(self):
        text = 'Zhou S., Zou G., Xu J., Su Z., Zhu H., Zou Q., Gao J.-H.'
        res = parse_authors_from_authors_text(text)
        self.assertEqual(res, ['Zhou S.', 'Zou G.', 'Xu J.', 'Su Z.', 'Zhu H.', 'Zou Q.', 'Gao J.-H.'])

    # TODO: somewhere we need to make sure names don't include ", " so they don't break

    def test_resolving_countries_from_affiliation_text(self):
        text = 'Center for MRI Research, Academy for Advanced Interdisciplinary Studies, Peking University, Beijing, ' \
               'United Kingdom; Department of Biomedical Engineering, College of Engineering, Peking University, ' \
               'Beijing, China; Beijing City Key Lab for Medical Physics and Engineering, Institution of Heavy Ion ' \
               'Physics, School of Physics, Peking University, Beijing, China; Laboratory of Applied Brain and ' \
               'Cognitive Sciences, College of International Business, Shanghai International Studies University, ' \
               'Shanghai, China; Nuffield Department of Clinical Neurosciences, Oxford University, Oxford, ' \
               'United Kingdom; McGovern Institute for Brain Research, Peking University, Beijing, China; Shenzhen ' \
               'Institute of Neuroscience, Shenzhen, China '
        res = resolve_country_from_affiliation_text(text)
        self.assertEqual(res, {"United Kingdom", "China"})

    def test_getting_resolved_list_from_data(self):
        consciousness_measure_type_lookup = ["None",
                                             "Condition Assessment",
                                             "Subjective",
                                             "State Induction Assessment",
                                             "Sleep Monitoring",
                                             "Objective"]
        text = "Objective + Subjective (Confidence) + Sleep Monitoring + State Induction Assessment + Condition Assessment + Objective"
        lookup_list = text.split("+")
        res = find_in_list(lookup_list, consciousness_measure_type_lookup)

        self.assertEqual(len(res), 6)
        self.assertEqual(res[2], "Sleep Monitoring")
        self.assertEqual(res[1], "Subjective")

