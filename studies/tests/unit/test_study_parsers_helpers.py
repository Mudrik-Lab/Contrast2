from unittest import TestCase

from studies.parsers.studies_parsing_helpers import parse_authors_from_authors_text, \
    resolve_country_from_affiliation_text, parse_consciousness_measure_type_from_data, TypeFromData


class StudyParserHelpersTestCase(TestCase):
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

    def test_resolving_consciousness_measure_type_from_data(self):
        text = "Objective + Subjective (Confidence) + Sleep Monitoring + State Induction Assessment + Condition + Assessment + Objective"
        res = parse_consciousness_measure_type_from_data(text)
        self.assertEqual(len(res), 7)
        self.assertEqual(res[0], TypeFromData('Objective', ''))
        self.assertEqual(res[1], TypeFromData('Subjective', 'Confidence'))
