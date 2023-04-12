import json
import os
import unittest
from typing import Dict, Any

from studies.parsers.historic_data_helpers import find_in_list
from studies.parsers.parsing_findings_Contrast2 import parse
from studies.parsers.process_row import process_row, create_experiment, create_study, get_list_from_excel
from studies.parsers.studies_parsing_helpers import parse_authors_from_authors_text, \
    resolve_country_from_affiliation_text
from contrast_api.tests.base import BaseTestCase

test_file_path = "studies/data/test_data.xlsx"


def test_data_doesnt_exist():
    return not os.path.exists(
        os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), "data/test_data.xlsx"))


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

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_process_row(self):
        studies_data = self.given_studies_exist(test_file_path,
                                                sheet_name='test_studies')
        test_data_list = get_list_from_excel(test_file_path, sheet_name='test_data')

        for item in test_data_list:
            try:
                process_row(item=item)
            except:
                print(json.dumps(item))
                raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_Early_bilateral(self):
        studies_data = self.given_studies_exist('studies/data/test_data.xlsx',
                                                sheet_name='test_studies')
        item = {"Paper.Title": "Early bilateral and massive compromise of the frontal lobes", "Paper.DOI": "10.1016/j.nicl.2018.02.026", "# Exp": 1, "Experimental paradigms.Main Paradigm": "Case Study + Cognitive Tasks", "Experimental paradigms.Specific Paradigm": "Bilateral Frontal Affectation (Case Study) + Executive Control (Cognitive Tasks) + Memory (Cognitive Tasks) + Language (Cognitive Tasks)", "Experimental paradigms.Report": 1, "Sample.Type": "3 (Bilateral Frontal Affectation Patients)", "Sample.Total": "1 (1 Bilateral Frontal Affectation Patients)", "Sample.Included": 1, "Task.Description": "The subject underwent neuropsychological examination in which a battery of neuropsychological functions were used to evaluate attention (visual and auditory), memory encoding, language, praxis, and emotional processing.", "Task.Code": "7 (Match to Sample) + 33", "Should be included?": 1, "Stimuli Features.Categories": "Animals + Digits + Letters", "Stimuli Features.Description": "The patient underwent Assessment of visual and auditory cognitive functions using images of rabbits, digits and letters", "Stimuli Features.Modality": "Visual + Visual + Visual", "Stimuli Features.Duration": "None + None + None", "Stimuli Features.Contrast": "", "Measures of consciousness.Phase": "Pre Experiment", "Measures of consciousness.Type": "Condition Assessment", "Measures of consciousness.Description": "The participant underwent cognitive and perceptual tasks aimed at assessing her level of consciousness", "State - Content": 0, "Techniques": "fMRI + MRI", "Findings.Summary": "(1) The findings of preserved consciousness, primary and phenomenal consciousness, is taken to refute theories that assign a significant role for the frontal lobes in consciousness and specifically considered incompatible with HOT.", "Findings.NCC Tags": "-0 (Frontal Lobe <fMRI, MRI># Bilateral Frontal Affectation preserved consciousness)", "Findings.Measures": "9 (structural connectivity, DTI) + 1 + 34", "Encoding Notes": "", "Interpretation.GNW": "X", "Interpretation.IIT": 1, "Interpretation.RPT": "X", "Interpretation.HOT": 0, "Affiliation": "X", "Theory Driven": "1 (HOT)", "Internal Replication [0 = Not, 1=Internal Replication]": 0.0, "Findings.Spatial AAL Mapping": ""}

        try:
            process_row(item=item)
        except:
            raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_hidden_characters(self):
        item: dict[str | Any, str | int | Any] = {
            'Paper.Title': 'Combined behavioral and electrophysiological evidence for a direct cortical effect of prefrontal tDCS on disorders of consciousness',
            'Paper.DOI': '10.1038/s41598-020-61180-2', '# Exp': 1,
            'Experimental paradigms.Main Paradigm': 'Direct Stimulation + Disorders of Consciousness ',
            'Experimental paradigms.Specific Paradigm': 'tDCS (Direct Stimulation, anodal left DLPFC) + UW (Disorders of Consciousness) + MCS (Disorders of Consciousness) + Emergence from MCS (Disorder of Consciousness)',
            'Experimental paradigms.Report': 0, 'Sample.Type': '3 (UWS & MCS & EMCS)', 'Sample.Total': 69,
            'Sample.Included': 60,
            'Task.Description': 'Auditory regularities during oddball paradigm: Patients were instructed to actively count the occurrence of auditory oddballs (series of 4 identical tones followed by a 5th\n distinct tone; 20% of trials) delivered randomly among series of 5 identical tones (standard trials; 80% of trials).',
            'Task.Code': 9, 'Should be included?': 1, 'Stimuli Features.Categories': 'Tones',
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

        studies_data = self.given_studies_exist(test_file_path,
                                                sheet_name='test_studies')
        try:
            process_row(item=item)
        except:
            raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_ncc_finding(self):
        item = {
            'Paper.Title': 'Alpha electroencephalographic activity during rapid eye movement sleep in the spider monkey (Ateles geoffroyi) An index of arousal during sleep',
            'Paper.DOI': '10.1002/jez.2220', '# Exp': 1, 'Experimental paradigms.Main Paradigm': 'Sleep',
            'Experimental paradigms.Specific Paradigm': '', 'Experimental paradigms.Report': 0,
            'Sample.Type': '5 (Monkeys)', 'Sample.Total': 6, 'Sample.Included': 6,
            'Task.Description': 'no task. rs-EEG', 'Task.Code': 0, 'Should be included?': 1,
            'Stimuli Features.Categories': 'None', 'Stimuli Features.Description': 'None',
            'Stimuli Features.Modality': 'None', 'Stimuli Features.Duration': 'None',
            'Stimuli Features.Contrast': 'None', 'Measures of consciousness.Phase': 'Trial By Trial',
            'Measures of consciousness.Type': 'Sleep Monitoring',
            'Measures of consciousness.Description': 'The consciousness state was classified according to the EEG activity + EMG and EOG activity (standard classification)',
            'State - Content': 0, 'Techniques': 'EEG',
            'Findings.Summary': '(1) The results show that in the alpha frequency in electrodes O1-2 and F4 the relative power was higher than in wakefulness.\n (2) Phase coherence between O1-2 electrodes and F3 electrode was higher for REM sleep compared with NREM sleep.\n \n The phase coherence between posterior O1-2 electrodes and F3 considered prefrontal electrode is taken as supporting consciousness',
            'Findings.NCC Tags': '3 (600-800ms) + 14 (Power Neg 8-12Hz <!500-0ms># prestimulus alpha negatively correlated with consciousness) + 16 (centro-parietal electrode cluster Cz, CP1, CP2, P3, Pz, P4# for the P3b LPC component)',
            'Findings.Measures': '2 + 5 (phase coherence) + 9 (functional connectivity, phase coherence)',
            'Encoding Notes': 'Only bipolar O1-O2 and referential C3, C4, F3, and F4 were recorded. Only findings that were interpreted as relevant for consciousness were encoded.',
            'Interpretation.GNW': 1, 'Interpretation.IIT': 'X', 'Interpretation.RPT': 'X', 'Interpretation.HOT': 'X',
            'Affiliation': 'X', 'Theory Driven': 0, 'Internal Replication [0 = Not, 1=Internal Replication]': 0,
            'Findings.Spatial AAL Mapping': ''}
        studies_data = self.given_studies_exist(test_file_path,
                                                sheet_name='test_studies')
        try:
            process_row(item=item)
        except:
            raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_sample_data(self):
        item: dict[str | Any, str | int | Any] = {
            'Paper.Title': 'Correlation between resting state fMRI total neuronal activity and PET metabolism in healthy controls and patients with disorders of consciousness',
            'Paper.DOI': '10.1002/brb3.424', '# Exp': 1,
            'Experimental paradigms.Main Paradigm': 'Disorders of Consciousness + Resting State + Locked In Syndrome',
            'Experimental paradigms.Specific Paradigm': 'Unresponsive Wakefulness Syndrome (Disorders of Consciousness)+ Minimal Consciousness State (Disorders of Consciousness)',
            'Experimental paradigms.Report': 0, 'Sample.Type': '3 (UWS Patients & LIS Patients & Healthy Controls)',
            'Sample.Total': '31 (16 Healthy Controls + 11 UWS Patients + 4 LIS Patients)', 'Sample.Included': 31,
            'Task.Description': 'no task - resting state', 'Task.Code': 0, 'Should be included?': 1,
            'Stimuli Features.Categories': 'None', 'Stimuli Features.Description': 'None',
            'Stimuli Features.Modality': 'None', 'Stimuli Features.Duration': 'None',
            'Stimuli Features.Contrast': 'None', 'Measures of consciousness.Phase': 'Pre Experiment',
            'Measures of consciousness.Type': 'Condition Assessment',
            'Measures of consciousness.Description': 'Subjects were classified to consciousness states according to neurological evaluations using the CRS-R scale.',
            'State - Content': 0, 'Techniques': 'fMRI + PET',
            'Findings.Summary': '(1) both scans (rs-fMRI and PET) of patients showed decreased activity in medial and lateral fronto-parietal network (precuneus, mesiofrontal, bilateral\n posterior parietal, superior temporal, and dorsolateral prefrontal cortices). Taken as evidence compatible with GNW\n  (2) LIS patients group was too small for statistical analysis (according to authors N=4) yet also showed similar activity in the fronto-parietal network as in healthy controls.',
            'Findings.NCC Tags': '16 (precuneus <fMRI>& precuneus <PET> & temporo-parietal junction <fMRI>& temporo-parietal junction <PET>) + 0 (medial prefrontal cortex <fMRI>& medial prefrontal cortex <PET> & inferior frontal gyrus <fMRI>& inferior frontal gyrus <PET> & medial frontal gyrus <fMRI>& medial frontal gyrus <PET>)',
            'Findings.Measures': '27 + 1 + 0 (MVPA, SVM)', 'Encoding Notes': '', 'Interpretation.GNW': 1,
            'Interpretation.IIT': 'X', 'Interpretation.RPT': 'X', 'Interpretation.HOT': 'X', 'Affiliation': 'X',
            'Theory Driven': 0, 'Internal Replication [0 = Not, 1=Internal Replication]': 0,
            'Findings.Spatial AAL Mapping': 'Precuneus_L <precuneus 0,-56,13> + Parietal_Inf_R<temporo-parietal junction 46,-40,46> + Frontal_Inf_Tri_L <medial frontal cortex -48,12,26> + Frontal_Inf_Oper_L<inferior frontal gyrus -54,13,15>'}
        studies_data = self.given_studies_exist(test_file_path,
                                                sheet_name='test_studies')
        try:
            process_row(item=item)
        except:
            raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_Unresponsive_Wakefulness_Syndrome(self):
        item: dict[str | Any, str | int | Any] = {
            'Paper.Title': 'Correlation between resting state fMRI total neuronal activity and PET metabolism in healthy controls and patients with disorders of consciousness',
            'Paper.DOI': '10.1002/brb3.424', '# Exp': 1,
            'Experimental paradigms.Main Paradigm': 'Disorders of Consciousness + Resting State + Locked In Syndrome',
            'Experimental paradigms.Specific Paradigm': 'Unresponsive Wakefulness Syndrome (Disorders of Consciousness)+ Minimal Consciousness State (Disorders of Consciousness)',
            'Experimental paradigms.Report': 0, 'Sample.Type': '3 (UWS Patients & LIS Patients & Healthy Controls)',
            'Sample.Total': '31 (16 Healthy Controls + 11 UWS Patients + 4 LIS Patients)', 'Sample.Included': 31,
            'Task.Description': 'no task - resting state', 'Task.Code': 0, 'Should be included?': 1,
            'Stimuli Features.Categories': 'None', 'Stimuli Features.Description': 'None',
            'Stimuli Features.Modality': 'None', 'Stimuli Features.Duration': 'None',
            'Stimuli Features.Contrast': 'None', 'Measures of consciousness.Phase': 'Pre Experiment',
            'Measures of consciousness.Type': 'Condition Assessment',
            'Measures of consciousness.Description': 'Subjects were classified to consciousness states according to neurological evaluations using the CRS-R scale.',
            'State - Content': 0, 'Techniques': 'fMRI + PET',
            'Findings.Summary': '(1) both scans (rs-fMRI and PET) of patients showed decreased activity in medial and lateral fronto-parietal network (precuneus, mesiofrontal, bilateral\n posterior parietal, superior temporal, and dorsolateral prefrontal cortices). Taken as evidence compatible with GNW\n  (2) LIS patients group was too small for statistical analysis (according to authors N=4) yet also showed similar activity in the fronto-parietal network as in healthy controls.',
            'Findings.NCC Tags': '16 (precuneus <fMRI>& precuneus <PET> & temporo-parietal junction <fMRI>& temporo-parietal junction <PET>) + 0 (medial prefrontal cortex <fMRI>& medial prefrontal cortex <PET> & inferior frontal gyrus <fMRI>& inferior frontal gyrus <PET> & medial frontal gyrus <fMRI>& medial frontal gyrus <PET>)',
            'Findings.Measures': '27 + 1 + 0 (MVPA, SVM)', 'Encoding Notes': '', 'Interpretation.GNW': 1,
            'Interpretation.IIT': 'X', 'Interpretation.RPT': 'X', 'Interpretation.HOT': 'X', 'Affiliation': 'X',
            'Theory Driven': 0, 'Internal Replication [0 = Not, 1=Internal Replication]': 0,
            'Findings.Spatial AAL Mapping': 'Precuneus_L <precuneus 0,-56,13> + Parietal_Inf_R<temporo-parietal junction 46,-40,46> + Frontal_Inf_Tri_L <medial frontal cortex -48,12,26> + Frontal_Inf_Oper_L<inferior frontal gyrus -54,13,15>'}
        studies_data = self.given_studies_exist(test_file_path,
                                                sheet_name='test_studies')
        try:
            process_row(item=item)
        except:
            raise AssertionError

    def given_studies_exist(self, path, sheet_name):
        test_studies = get_list_from_excel(path, sheet_name)
        studies_data = []
        for study_item in test_studies:
            try:
                study = create_study(item=study_item)
                studies_data.append(study)
            except:
                print(json.dumps(study_item))
                raise AssertionError()

        return studies_data
