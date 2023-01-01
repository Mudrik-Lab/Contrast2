from unittest import TestCase

from studies.studies_parsing_helpers import parse_authors_from_affiliation_text, resolve_country_from_affiliation_text


class StudyParserHelpersTestCase(TestCase):
    def test_parsing_authors_from_affiliation_text(self):
        text = 'Zhou S., Zou G., Xu J., Su Z., Zhu H., Zou Q., Gao J.-H.'
        res = parse_authors_from_affiliation_text(text)
        self.assertEqual(res, ['Zhou S.', 'Zou G.', 'Xu J.', 'Su Z.', 'Zhu H.', 'Zou Q.', 'Gao J.-H.'])

    def test_resolving_countries_from_affiliation_text(self):
        text = 'Center for MRI Research, Academy for Advanced Interdisciplinary Studies, Peking University, Beijing, United Kingdom; Department of Biomedical Engineering, College of Engineering, Peking University, Beijing, China; Beijing City Key Lab for Medical Physics and Engineering, Institution of Heavy Ion Physics, School of Physics, Peking University, Beijing, China; Laboratory of Applied Brain and Cognitive Sciences, College of International Business, Shanghai International Studies University, Shanghai, China; Nuffield Department of Clinical Neurosciences, Oxford University, Oxford, United Kingdom; McGovern Institute for Brain Research, Peking University, Beijing, China; Shenzhen Institute of Neuroscience, Shenzhen, China'
        res = resolve_country_from_affiliation_text(text)
        self.assertEqual(res, ["United Kingdom", "China"])
