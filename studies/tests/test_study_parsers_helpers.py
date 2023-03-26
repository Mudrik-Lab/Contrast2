from typing import Dict, Any
from unittest import TestCase

import numpy
import pandas
from configurations.management import call_command

from studies.models import Study
from studies.parsers.historic_data_helpers import find_in_list
from studies.parsers.parsing_findings_Contrast2 import parse
from studies.parsers.process_row import process_row, create_experiment, create_study, get_list_from_excel
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

    def test_process_row(self):
        test_data_list = get_list_from_excel('studies/data/test_data.xlsx', sheet_name='test_data')
        studies_data = self.given_studies_exist('studies/data/test_data.xlsx',
                                                sheet_name='test_studies')
        for item in test_data_list:
            # experiment, theory_driven_theories = create_experiment(item)
            try:
                process_row(item=item)
            except:
                print(item)

    def test_GABA_agonist(self):
        item = {'Paper.Title': 'GABA A agonist reduces visual awareness A masking-EEG experiment',
                'Paper.DOI': '10.1162/jocn_a_00197', '# Exp': 1,
                'Experimental paradigms.Main Paradigm': 'Sedation + Masking + Figure-Ground',
                'Experimental paradigms.Specific Paradigm': 'Dextromethorphan (Sedation) + Lorazepam (Sedation) + Scopolamine (Sedation) + Backward Masking (Masking)',
                'Experimental paradigms.Report': 1, 'Sample.Type': 0, 'Sample.Total': 22, 'Sample.Included': 20,
                'Task.Description': 'The participants were asked to discriminate whether the target stimulus was homogenous / figure ground.\n Drug interventions were manipulated within subjects (1 week between sessions) with the drugs lorazepam (LZP), two control drugs and placebo. (2AFC)',
                'Task.Code': 1, 'Should be included?': 1, 'Stimuli Features.Categories': 'Textures',
                'Stimuli Features.Description': "Figure-Ground textures - line elements created the figure ground conditions.\n Masks were also parametrically manipulated to create masking conditions. No mask condition was an isoilluminante gray mask, mask was a texture-defined pattern mask with various strength (changing the gray level from black to light gray to create 11 masking strength).\n The authors defined a 'Subjective Mask' as the masks that was selected based on performance in the task to achieve 75% decrease in visibility according to behavioral measures, out of the intermediate mask conditions.",
                'Stimuli Features.Modality': 'Visual', 'Stimuli Features.Duration': '17ms',
                'Stimuli Features.Contrast': "varied to achieve 75% performance on the 'subjective mask' condition",
                'Measures of consciousness.Phase': 'Trial By Trial',
                'Measures of consciousness.Type': 'Objective + State Induction Assessment',
                'Measures of consciousness.Description': 'Before the main experiment in a practice session the subjective mask condition was selected + trial by trial the main task can be considered as an objective measure o consciousness of the figure.\n In addition the state of sedation was measured by a subjective measure (visual analogue scales)',
                'State - Content': 2, 'Techniques': 'EEG',
                'Findings.Summary': '(1) both masking and LPZ (and not control/placebo drugs) decreased the amplitude of intermediate (~156-211ms) and late time windows (293-386ms) activity in the relevant electrodes (occipital), while for both, early (94-121ms) activity was relatively intact. this is taken as evidence for recurrent processing as the mechanism being impaired in both masking and LPZ admission and the crucial role of recurrent processing in visual awareness.\n (2) masking strength correlated linearly with the intermediate time window (VAN) eeg activity. (with LPZ the activity was decreased and this effect was not pronounced)\n (3) Late positivity was not modulated by masking strength and was less effected by LPZ. this is taken as evidence against GNW\n (4) Recurrent processing that was impaired due to LPZ was dependent on GABAergic interneurons.',
                'Findings.NCC Tags': '4 (156-211ms) + 21 (Occipital and parietal electrodes &) + -3 (293-386ms) + 7 + 24',
                'Findings.Measures': '3 (Cluster)+ 6 + 52 (Awareness, visual analogue scale)', 'Encoding Notes': '',
                'Interpretation.GNW': 0, 'Interpretation.IIT': 'X', 'Interpretation.RPT': 1, 'Interpretation.HOT': 'X',
                'Affiliation': 'RPT', 'Theory Driven': '2 (RPT)',
                'Internal Replication [0 = Not, 1=Internal Replication]': 0, 'Findings.Spatial AAL Mapping': ''}
        studies_data = self.given_studies_exist('studies/data/test_data.xlsx',
                                                sheet_name='test_studies')
        process_row(item=item)

    def test_hidden_characters(self):
        item = {
            'Paper.Title': 'Late Positivity Does Not Meet the Criteria to be Considered a Proper Neural Correlate of Perceptual Awareness',
            'Paper.DOI': '10.3389/fnsys.2020.00036', '# Exp': 1,
            'Experimental paradigms.Main Paradigm': 'Stimulus Degradation',
            'Experimental paradigms.Specific Paradigm': 'Intensity Reduction (Stimulus Degradation)',
            'Experimental paradigms.Report': 1, 'Sample.Type': 0, 'Sample.Total': 59, 'Sample.Included': 24,
            'Task.Description': "participants were requested to discriminate the orientation of a Gabor, chosing: Verticle, Horizontal. I don't know. Two conditions: 1) conservative session - participants were instructed to report the Gabor orientation only if they clearly perceived it. 2) The liberal session, participants were asked to report the orientation of the stimulus whenever they had a minimal impression.",
            'Task.Code': 1, 'Should be included?': 1, 'Stimuli Features.Categories': 'Gratings \u200e(Gabor)',
            'Stimuli Features.Description': 'vertically or horizontally oriented sinusoidal Gabor patches of about 4 degree of visual angle',
            'Stimuli Features.Modality': 'Visual', 'Stimuli Features.Duration': '36ms', 'Stimuli Features.Contrast': 1,
            'Measures of consciousness.Phase': 'Trial By Trial',
            'Measures of consciousness.Type': 'Objective + Subjective',
            'Measures of consciousness.Description': 'Aware vs. not aware of the Gabors direction (Objective) + confidence level (Subjective_',
            'State - Content': 1, 'Techniques': 'EEG',
            'Findings.Summary': 'Contrasting conservative, and liberal, criterion and aware vs not aware: negative deflection (VAN) at posterior temporal electrodes, followed by positive enhancement at centro-parietal sites.\n Criterion effect was found in N1 under conservative criterion. P3 was greater under liberal criterion.\n An interacion was found for LP between awereness and criterion but not for VAN.',
            'Findings.NCC Tags': '4(204-228ms#, posterior temporal electrodes O1, Oz, O2, PO7, PO8, and P7, aware vs unaware) + 21(VAN# 204-228ms, electrods O1, Oz, O2, PO7, PO8, and P7, aware vs unaware) + 3(328-676ms# all electrodes except for Fp1, Fp2, AF7, AF3, AF8, F7, F5, F3, and FT7, aware vs unaware) + 39(152-180 #central and posterior electrodes Cz, C2, CP5, CP3, CP1, CPz, CP2, CP4, CP6, P3, P1, Pz, P2, P4, P6, PO3, POz, PO4, and Oz, higher in conservative critirion) + 16(N1 centro posterior electrodes Cz, C2, CP5, CP3, CP1, CPz, CP2, CP4, CP6, P3, P1, Pz, P2, P4, P6, PO3, POz, PO4, and Oz, higher in conservative critirion) + 0(N1 centro posterior electrodes Cz, C2, CP5, CP3, CP1, CPz, CP2, CP4, CP6, P3, P1, Pz, P2, P4, P6, PO3, POz, PO4, and Oz, higher in conservative critirion) + 3(332-560ms# greater for liberal criterior, mostly central and parietal electrods, mainly) + 0(P3, 332-560, cetro-parietal electrods, liberal criterior) + 16(P3, 332-560, cetro-parietal electrods, liberal criterior) -3(500-800ms #interaction between awareness and criterion)',
            'Findings.Measures': 3, 'Encoding Notes': '', 'Interpretation.GNW': 0, 'Interpretation.IIT': 'X',
            'Interpretation.RPT': 'X', 'Interpretation.HOT': 'X', 'Affiliation': 'X', 'Theory Driven': '1(GNW)',
            'Internal Replication [0 = Not, 1=Internal Replication]': 0, 'Findings.Spatial AAL Mapping': ''}

        studies_data = self.given_studies_exist('studies/data/test_data.xlsx',
                                                sheet_name='test_studies')
        res = process_row(item=item)

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
        studies_data = self.given_studies_exist('studies/data/test_data.xlsx',
                                                sheet_name='test_studies')
        process_row(item=item)

    def test_sample_data(self):
        item: dict[str | Any, str | int | Any] = {'Paper.Title': 'Correlation between resting state fMRI total neuronal activity and PET metabolism in healthy controls and patients with disorders of consciousness', 'Paper.DOI': '10.1002/brb3.424', '# Exp': 1, 'Experimental paradigms.Main Paradigm': 'Disorders of Consciousness + Resting State + Locked In Syndrome', 'Experimental paradigms.Specific Paradigm': 'Unresponsive Wakefulness Syndrome (Disorders of Consciousness)+ Minimal Consciousness State (Disorders of Consciousness)', 'Experimental paradigms.Report': 0, 'Sample.Type': '3 (UWS Patients & LIS Patients & Healthy Controls)', 'Sample.Total': '31 (16 Healthy Controls + 11 UWS Patients + 4 LIS Patients)', 'Sample.Included': 31, 'Task.Description': 'no task - resting state', 'Task.Code': 0, 'Should be included?': 1, 'Stimuli Features.Categories': 'None', 'Stimuli Features.Description': 'None', 'Stimuli Features.Modality': 'None', 'Stimuli Features.Duration': 'None', 'Stimuli Features.Contrast': 'None', 'Measures of consciousness.Phase': 'Pre Experiment', 'Measures of consciousness.Type': 'Condition Assessment', 'Measures of consciousness.Description': 'Subjects were classified to consciousness states according to neurological evaluations using the CRS-R scale.', 'State - Content': 0, 'Techniques': 'fMRI + PET', 'Findings.Summary': '(1) both scans (rs-fMRI and PET) of patients showed decreased activity in medial and lateral fronto-parietal network (precuneus, mesiofrontal, bilateral\n posterior parietal, superior temporal, and dorsolateral prefrontal cortices). Taken as evidence compatible with GNW\n  (2) LIS patients group was too small for statistical analysis (according to authors N=4) yet also showed similar activity in the fronto-parietal network as in healthy controls.', 'Findings.NCC Tags': '16 (precuneus <fMRI>& precuneus <PET> & temporo-parietal junction <fMRI>& temporo-parietal junction <PET>) + 0 (medial prefrontal cortex <fMRI>& medial prefrontal cortex <PET> & inferior frontal gyrus <fMRI>& inferior frontal gyrus <PET> & medial frontal gyrus <fMRI>& medial frontal gyrus <PET>)', 'Findings.Measures': '27 + 1 + 0 (MVPA, SVM)', 'Encoding Notes': '', 'Interpretation.GNW': 1, 'Interpretation.IIT': 'X', 'Interpretation.RPT': 'X', 'Interpretation.HOT': 'X', 'Affiliation': 'X', 'Theory Driven': 0, 'Internal Replication [0 = Not, 1=Internal Replication]': 0, 'Findings.Spatial AAL Mapping': 'Precuneus_L <precuneus 0,-56,13> + Parietal_Inf_R<temporo-parietal junction 46,-40,46> + Frontal_Inf_Tri_L <medial frontal cortex -48,12,26> + Frontal_Inf_Oper_L<inferior frontal gyrus -54,13,15>'}
        studies_data = self.given_studies_exist('studies/data/test_data.xlsx',
                                                sheet_name='test_studies')
        process_row(item=item)

    def test_Unresponsive_Wakefulness_Syndrome(self):
        item: dict[str | Any, str | int | Any] = {'Paper.Title': 'Correlation between resting state fMRI total neuronal activity and PET metabolism in healthy controls and patients with disorders of consciousness', 'Paper.DOI': '10.1002/brb3.424', '# Exp': 1, 'Experimental paradigms.Main Paradigm': 'Disorders of Consciousness + Resting State + Locked In Syndrome', 'Experimental paradigms.Specific Paradigm': 'Unresponsive Wakefulness Syndrome (Disorders of Consciousness)+ Minimal Consciousness State (Disorders of Consciousness)', 'Experimental paradigms.Report': 0, 'Sample.Type': '3 (UWS Patients & LIS Patients & Healthy Controls)', 'Sample.Total': '31 (16 Healthy Controls + 11 UWS Patients + 4 LIS Patients)', 'Sample.Included': 31, 'Task.Description': 'no task - resting state', 'Task.Code': 0, 'Should be included?': 1, 'Stimuli Features.Categories': 'None', 'Stimuli Features.Description': 'None', 'Stimuli Features.Modality': 'None', 'Stimuli Features.Duration': 'None', 'Stimuli Features.Contrast': 'None', 'Measures of consciousness.Phase': 'Pre Experiment', 'Measures of consciousness.Type': 'Condition Assessment', 'Measures of consciousness.Description': 'Subjects were classified to consciousness states according to neurological evaluations using the CRS-R scale.', 'State - Content': 0, 'Techniques': 'fMRI + PET', 'Findings.Summary': '(1) both scans (rs-fMRI and PET) of patients showed decreased activity in medial and lateral fronto-parietal network (precuneus, mesiofrontal, bilateral\n posterior parietal, superior temporal, and dorsolateral prefrontal cortices). Taken as evidence compatible with GNW\n  (2) LIS patients group was too small for statistical analysis (according to authors N=4) yet also showed similar activity in the fronto-parietal network as in healthy controls.', 'Findings.NCC Tags': '16 (precuneus <fMRI>& precuneus <PET> & temporo-parietal junction <fMRI>& temporo-parietal junction <PET>) + 0 (medial prefrontal cortex <fMRI>& medial prefrontal cortex <PET> & inferior frontal gyrus <fMRI>& inferior frontal gyrus <PET> & medial frontal gyrus <fMRI>& medial frontal gyrus <PET>)', 'Findings.Measures': '27 + 1 + 0 (MVPA, SVM)', 'Encoding Notes': '', 'Interpretation.GNW': 1, 'Interpretation.IIT': 'X', 'Interpretation.RPT': 'X', 'Interpretation.HOT': 'X', 'Affiliation': 'X', 'Theory Driven': 0, 'Internal Replication [0 = Not, 1=Internal Replication]': 0, 'Findings.Spatial AAL Mapping': 'Precuneus_L <precuneus 0,-56,13> + Parietal_Inf_R<temporo-parietal junction 46,-40,46> + Frontal_Inf_Tri_L <medial frontal cortex -48,12,26> + Frontal_Inf_Oper_L<inferior frontal gyrus -54,13,15>'}
        studies_data = self.given_studies_exist('studies/data/test_data.xlsx',
                                                sheet_name='test_studies')
        try:
            process_row(item=item)
        except:
            print(item)
            raise AssertionError



    def given_studies_exist(self, path, sheet_name):
        test_studies = get_list_from_excel(path, sheet_name)
        studies_data = [create_study(item=study_item) for study_item in test_studies]

        return studies_data
