import json
from typing import Any

from studies.parsers.historic_data_helpers import find_in_list
from studies.parsers.parsing_findings_Contrast2 import parse
from studies.parsers.process_row import process_row, create_study
from studies.parsers.studies_parsing_helpers import parse_authors_from_authors_text, \
    resolve_country_from_affiliation_text
from contrast_api.tests.base import BaseTestCase


class StudyParserHelpersTestCase(BaseTestCase):
    def test_parsing_authors_from_affiliation_text(self):
        text = 'Zhou S., Zou G., Xu J., Su Z., Zhu H., Zou Q., Gao J.-H.'
        res = parse_authors_from_authors_text(text)
        self.assertEqual(res, ['Zhou S.', 'Zou G.', 'Xu J.', 'Su Z.', 'Zhu H.', 'Zou Q.', 'Gao J.-H.'])

    # TODO: somewhere we need to make sure names don't include ", " so they don't break

    def test_resolving_countries_from_affiliation_text(self):
        text = 'Department of Physiology and Pharmacology, Sackler School of Medicine, Tel Aviv University, Tel Aviv, 6997801, Israel; Department of Anesthesiology and Critical Care Medicine, Hadassah-Hebrew University Medical Center, Jerusalem, 91120, Israel; Hadassah School of Medicine, Hebrew University, Jerusalem, 91120, Israel; Sagol School of Neuroscience, Tel Aviv University, Tel Aviv, 6997801, Israel; Functional Neurosurgery Unit, Tel Aviv Sourasky Medical Center, Tel Aviv, 6423906, Israel; Department of Neurology and Neurosurgery, Sackler School of Medicine, Tel Aviv University, Tel Aviv, 6997801, Israel; Department of Anesthesia, Intensive Care and Pain, Tel Aviv Medical Center, Sackler Medical School, Tel Aviv University, Tel Aviv, 6997801, Israel; EEG and Epilepsy Unit, Department of Neurology, Tel Aviv Sourasky Medical Center, Tel Aviv, 6423906, Israel; Department of Anesthesiology and Intensive Care Medicine, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Neurosurgery, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Epileptology, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Neurosurgery, University of California, Los Angeles, CA  90095, United States'
        res = resolve_country_from_affiliation_text(text)
        self.assertEqual(res, {"United States", "Israel", "Germany"})

    def test_getting_resolved_list_from_data(self):
        consciousness_measure_type_lookup = ["None",
                                             "Condition Assessment",
                                             "Subjective",
                                             "State Induction Assessment",
                                             "Sleep Monitoring",
                                             "Objective"]
        text1 = "Objective + Subjective (Confidence)"
        text2 = "Sleep Monitoring + State Induction Assessment"
        text3 = "Subjective + Objective"
        lookup_list1 = text1.split("+")
        lookup_list2 = text2.split("+")
        lookup_list3 = text3.split("+")
        res1 = find_in_list(lookup_list1, consciousness_measure_type_lookup)
        res2 = find_in_list(lookup_list2, consciousness_measure_type_lookup)
        res3 = find_in_list(lookup_list3, consciousness_measure_type_lookup)

        self.assertEqual(len(res1), 2)
        self.assertEqual(res1[0], "Objective")
        self.assertEqual(res3[1], "Objective")
        self.assertEqual(len(res3), 2)

    def test_finding_tag_parser(self):
        text = "50 (# The findings of frontal and posterior areas are reflecting significant differences between light" \
               " and deep sedation states in this measure) + 0 (medial PFC & Orbital PFC & dorsolateral PFC & Insular" \
               " Cortex &) + 21 (Temporal Pole &) + 8 (#frequency analysis of slow oscillations considered to reflect" \
               " long distance synchronization) + 42 (Amygdala & Hippocampus & Parahippocampal Gyrus)"
        res = parse(text)
        self.assertEqual(len(res), 10)

        text2 = "41(connectivity between A1 and ACC ) + 11 + 16 (posterior cingulate cortex# −5 −49 26)"
        res = parse(text2)
        self.assertEqual(len(res), 3)

        text3 = "5 (Connectivity 90-120Hz) + 7 (?) + 8 (Normalized Degree) + 6 (Dimension of activation) + 14 (Connectivity Neg 7-13Hz) + 38 (Normalized Degree)"
        res = parse(text3)
        self.assertEqual(len(res), 6)

        text4 = "-5 (Power 30-40Hz<340-420ms> # gamma activity reflected task relevance and not visibility)+ -3(380-550ms # P300 reflected task relevance and not visibility)"
        res = parse(text4)
        self.assertEqual(len(res), 2)

    def given_studies_exist(self, test_studies: list) -> list:
        studies_data = []
        for study_item in test_studies:
            try:
                study = create_study(item=study_item)
                studies_data.append(study)
            except:
                print(json.dumps(study_item))
                raise AssertionError()

        return studies_data

    def test_hidden_characters(self):
        test_studies = [{"DOI": "10.1038/s41598-020-61180-2", "Title": "Combined behavioral and electrophysiological evidence for a direct cortical effect of prefrontal tDCS on disorders of consciousness", "Year": 2020, "Authors": "Hermann B., Raimondo F., Hirsch L., Huang Y., Denis-Valente M., P\u00e9rez P., Engemann D., Faugeras F., Weiss N., Demeret S., Rohaut B., Parra L.C., Sitt J.D., Naccache L.", "Source.Title": "Scientific Reports", "Affiliations": "Institut du Cerveau et de la Moelle \u00e9pini\u00e8re, ICM, Paris, F-75013, France; Inserm U 1127, Paris, F-75013, France; CNRS UMR 7225, Paris, F-75013, France; Department of Neurology, Neuro ICU, H\u00f4pital de la Piti\u00e9-Salp\u00eatri\u00e8re, AP-HP, Paris, F-75013, France; Laboratorio de Inteligencia Artificial Aplicada, Departamento de Computaci\u00f3n FCEyN, UBA, Ciudad Aut\u00f3noma de Buenos Aires, C1428EGA, Argentina; CONICET \u2013 Universidad de Buenos Aires, Instituto de Investigaci\u00f3n en Ciencias de la Computaci\u00f3n, Godoy Cruz 2290, Ciudad Aut\u00f3noma de Buenos Aires, C1425FQB, Argentina; Biomedical Engineering Department, City College of the City University of New York, New York, NY  10031, United States; Department of Neurophysiology, H\u00f4pital de la Piti\u00e9-Salp\u00eatri\u00e8re, AP-HP, Paris, F-75013, France; Parietal project-team, INRIA, Universit\u00e9 Paris-Saclay, Saclay, 91120, France; Cognitive Neuroimaging Unit, CEA DSV/I2BM, INSERM, Universit\u00e9 Paris-Sud, Universit\u00e9 Paris-Saclay, NeuroSpin center, Gif-sur-Yvette, 91191, France; Facult\u00e9 de M\u00e9decine Piti\u00e9-Salp\u00eatri\u00e8re, Sorbonne Universit\u00e9, Paris, 75013, France; Department of Neurology, Columbia University, New York, NY  10027, United States", "Abstract": "Severe brain injuries can lead to long-lasting disorders of consciousness (DoC) such as vegetative state/unresponsive wakefulness syndrome (VS/UWS) or minimally conscious state (MCS). While behavioral assessment remains the gold standard to determine conscious state, EEG has proven to be a promising complementary tool to monitor the effect of new therapeutics. Encouraging results have been obtained with invasive electrical stimulation of the brain, and recent studies identified transcranial direct current stimulation (tDCS) as an effective approach in randomized controlled trials. This non-invasive and inexpensive tool may turn out to be the preferred treatment option. However, its mechanisms of action and physiological effects on brain activity remain unclear and debated. Here, we stimulated 60 DoC patients with the anode placed over left-dorsolateral prefrontal cortex in a prospective open-label study. Clinical behavioral assessment improved in twelve patients (20%) and none deteriorated. This behavioral response after tDCS coincided with an enhancement of putative EEG markers of consciousness: in comparison with non-responders, responders showed increases of power and long-range cortico-cortical functional connectivity in the theta-alpha band, and a larger and more sustained P300 suggesting improved conscious access to auditory novelty. The EEG changes correlated with electric fields strengths in prefrontal cortices, and no correlation was found on the scalp. Taken together, this prospective intervention in a large cohort of DoC patients strengthens the validity of the proposed EEG signatures of consciousness, and is suggestive of a direct causal effect of tDCS on consciousness. \u00a9 2020, The Author(s).", "Author.Keywords": "", "Funding.Details": "This work was supported by: \u2018e(ye)BRAIN, Ivry-sur-Seine, France\u2019, \u2018Institut National de la Sant\u00e9 et de la Recherche M\u00e9dicale\u2019 (BH, LN, JS), Sorbonne Universit\u00e9 (LN), the James S. McDonnell Foundation (LN), FRM 2015 (LN), UNIM (LN), Acad\u00e9mie des Sciences-Lamonica Prize 2016 (LN). The research leading to these results has received funding from the program \u2018Investissements d\u2019avenir\u2019 ANR-10-IAIHU-06, \u2018and by ANR grant \u2018CogniComa\u2019 (ANR-14-CE-0013-03). BH was funded by \u2018Poste d\u2019Accueil Inserm\u2019 grant.", "Abbreviated.Source.Title": "Sci. Rep."}]
        study = self.given_studies_exist(test_studies)[0]

        item: dict[str | Any, str | int | Any] = {
            'Paper.Title': 'Combined behavioral and electrophysiological evidence for a direct cortical effect of prefrontal tDCS on disorders of consciousness',
            'Paper.DOI': '10.1038/s41598-020-61180-2', '# Exp': 1,
            'Experimental paradigms.Main Paradigm': 'Direct Stimulation + Disorders of Consciousness ',
            'Experimental paradigms.Specific Paradigm': 'tDCS (Direct Stimulation, anodal left DLPFC) + UW (Disorders of Consciousness) + MCS (Disorders of Consciousness) + Emergence from MCS (Disorder of Consciousness)',
            'Experimental paradigms.Report': 0, 'Sample.Type': '3 (UWS & MCS & EMCS)', 'Sample.Total': 69,
            'Sample.Included': 60,
            'Task.Description': 'Auditory regularities during oddball paradigm: Patients were instructed to actively count the occurrence of auditory oddballs (series of 4 identical tones followed by a 5th\n distinct tone; 20% of trials) delivered randomly among series of 5 identical tones (standard trials; 80% of trials).',
            'Task.Code': 9, 'Should be included?': 1, 'Stimuli Features.Categories': 'Sounds (Tones)',
            'Stimuli Features.Description': '4 identical tones followed by a 5th distinct tone; (20% of trials) delivered randomly among series of 5 identical tones (standard trials; 80% of trials).',
            'Stimuli Features.Modality': 'Auditory', 'Stimuli Features.Duration': 'None',
            'Stimuli Features.Contrast': '', 'Measures of consciousness.Phase': 'Pre Experiment + Post Experiment',
            'Measures of consciousness.Type': 'Condition Assessment',
            'Measures of consciousness.Description': 'CRS-R (Pre & post Experiment) + EEG (rest & auditory oddball) (Per & Post Trial)',
            'State - Content': 0, 'Techniques': 'EEG + tDCS',
            'Findings.Summary': 'behavioral (CRS-R): 20% of patients responded positivly to tDCS (R+) & 3 patients shwoed change in conscious states. None of the patients showed decrease(R-) the rest of the patients stayed stable (also R-).\n EEG resting state in interation with (CRS-R):\n Power spectral: Post tDCS (and compared to R-) R+ increased normalized theta power over parietal cortices + Increase raw and normalized alpha\n Complexity: (PeEn in theta-alpha band) trends of increase in parietal.\n Functional connectivity: increase in parieto-occipital value in R+ vs. R-\n EEG auditory regularities during oddball:\n  R+ showed positive left lateralized anterior cluster spaning (vs. R-, comparing pre-post ERP from oddball task) from 28-376ms. (posterior cluster from 52-312ms & left-kateralized anterior cluster from 68-392ms) ERP started early but sustained and peaked and 200ms (P3).',
            'Findings.NCC Tags': '28(Power 4-8Hz) + 14(Power 8-12Hz#parietal) + 6(PeEn #Theta-Alpha parietal) + 41(parieto-occipital, 4-10Hz) + 28(Conectivity 4-8Hz) + 14(Connectivity 8-10Hz) + 3 (52-312ms#P3a peaked at 200ms, posterior) + 3(68-392ms# P3a peaked at 200ms, left-lateralized anterior)',
            'Findings.Measures': '2 (induced # power) +9(functional, SMI) + 14(PeEn) + 3 (cluster) + 0 (MVPA)',
            'Encoding Notes': '', 'Interpretation.GNW': 1, 'Interpretation.IIT': 'X', 'Interpretation.RPT': 'X',
            'Interpretation.HOT': 'X', 'Affiliation': 'X', 'Theory Driven': '2 (GNW)',
            'Internal Replication [0 = Not, 1=Internal Replication]': 0.0, 'Findings.Spatial AAL Mapping': ''}

        try:
            process_row(item=item)
        except:
            raise AssertionError()
