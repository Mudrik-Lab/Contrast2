import json
import os
import unittest
from typing import Any

from studies.parsers.historic_data_helpers import find_in_list
from studies.parsers.parsing_findings_Contrast2 import parse
from studies.parsers.process_row import process_row, create_study, get_list_from_excel
from studies.parsers.studies_parsing_helpers import parse_authors_from_authors_text, \
    resolve_country_from_affiliation_text
from contrast_api.tests.base import BaseTestCase

test_file_path = "studies/data/test_data.xlsx"


def test_data_doesnt_exist():
    return not (os.path.exists(
        os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), "data/test_data.xlsx")) or
                os.path.exists(
                    os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), "../data/test_data.xlsx"))
                )


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
        find_in_list(lookup_list2, consciousness_measure_type_lookup)
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
        self.given_studies_exist(test_file_path,
                                 sheet_name='test_studies')
        test_data_list = get_list_from_excel(test_file_path, sheet_name='test_data')

        for item in test_data_list:
            try:
                process_row(item=item)
            except Exception:
                print(json.dumps(item))
                raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_Cingulate_Mid_finding(self):
        self.given_studies_exist('studies/data/test_data.xlsx',
                                 sheet_name='test_studies')

        item: dict[str | Any, str | int | Any] = {
            "Paper.Title": "Pain-Evoked Reorganization in Functional Brain Networks",
            "Paper.DOI": "10.1093/cercor/bhz276", "# Exp": 1, "Experimental paradigms.Main Paradigm": "Pain",
            "Experimental paradigms.Specific Paradigm": "Pain", "Experimental paradigms.Report": 0, "Sample.Type": 0,
            "Sample.Total": 119, "Sample.Included": 106,
            "Task.Description": "participants received a series of contact-heat stimulus using a TSA-II Neurosensory Analyzer (Medoc Ltd) with a 16mmPeltier thermode endplate (Study 7:32 mm) and rated the magnitude of pain they felt on a visual analog scale (VAS) after stimulus offset. focus was on investigating the difference between noxious and innocuous stimuli in functional network organization, and all psychological manipulations were balanced across (orthogonal to) noxious and innocuous conditions. 45.3 \u25e6C was used as a threshold for dividing thermal stimulation into innocuous (stimulation intensity <45.3 \u25e6C) and noxious (stimulation intensity >45.3 \u25e6C) conditions.",
            "Task.Code": 0, "Should be included?": 1, "Stimuli Features.Categories": "Nociceptive stimulation",
            "Stimuli Features.Description": "innocuous (stimulation intensity <45.3 \u25e6C) and noxious (stimulation intensity >45.3 \u25e6C) conditions",
            "Stimuli Features.Modality": "Tactile", "Stimuli Features.Duration": "",
            "Stimuli Features.Contrast": "None", "Measures of consciousness.Phase": "Trial By Trial",
            "Measures of consciousness.Type": "Objective", "Measures of consciousness.Description": "None",
            "State - Content": "", "Techniques": "fMRI",
            "Findings.Summary": "pain integrates somatosensory activity with frontoparietal systems (the CCN here). cortical targets of nociceptive afferents (generally located in SMN and ION here) and frontoparietal systems (CCN). We found that all of these systems are integrated\n  during pain.",
            "Findings.NCC Tags": "9(Frontal_Inf_Oper_L & Cingulate_Mid_R & Frontal_Mid_L & Frontal_Sup_L)",
            "Findings.Measures": "9(functional)", "Encoding Notes": "", "Interpretation.GNW": 1,
            "Interpretation.IIT": "X", "Interpretation.RPT": "X", "Interpretation.HOT": "X", "Affiliation": "X",
            "Theory Driven": 0, "Internal Replication [0 = Not, 1=Internal Replication]": "",
            "Findings.Spatial AAL Mapping": "Frontal_Inf_Oper_L + Cingulum_Mid_R + Frontal_Mid_L + Frontal_Sup_L"}

        try:
            process_row(item=item)
        except Exception:
            raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_Early_bilateral(self):
        self.given_studies_exist(test_file_path,
                                 sheet_name='test_studies')
        item = {"Paper.Title": "Early bilateral and massive compromise of the frontal lobes",
                "Paper.DOI": "10.1016/j.nicl.2018.02.026", "# Exp": 1,
                "Experimental paradigms.Main Paradigm": "Case Study + Cognitive Tasks",
                "Experimental paradigms.Specific Paradigm": "Bilateral Frontal Affectation (Case Study) + Executive Control (Cognitive Tasks) + Memory (Cognitive Tasks) + Language (Cognitive Tasks)",
                "Experimental paradigms.Report": 1, "Sample.Type": "3 (Bilateral Frontal Affectation Patients)",
                "Sample.Total": "1 (1 Bilateral Frontal Affectation Patients)", "Sample.Included": 1,
                "Task.Description": "The subject underwent neuropsychological examination in which a battery of neuropsychological functions were used to evaluate attention (visual and auditory), memory encoding, language, praxis, and emotional processing.",
                "Task.Code": "7 (Match to Sample) + 33", "Should be included?": 1,
                "Stimuli Features.Categories": "Animals + Digits + Letters",
                "Stimuli Features.Description": "The patient underwent Assessment of visual and auditory cognitive functions using images of rabbits, digits and letters",
                "Stimuli Features.Modality": "Visual + Visual + Visual",
                "Stimuli Features.Duration": "None + None + None", "Stimuli Features.Contrast": "",
                "Measures of consciousness.Phase": "Pre Experiment",
                "Measures of consciousness.Type": "Condition Assessment",
                "Measures of consciousness.Description": "The participant underwent cognitive and perceptual tasks aimed at assessing her level of consciousness",
                "State - Content": 0, "Techniques": "fMRI + MRI",
                "Findings.Summary": "(1) The findings of preserved consciousness, primary and phenomenal consciousness, is taken to refute theories that assign a significant role for the frontal lobes in consciousness and specifically considered incompatible with HOT.",
                "Findings.NCC Tags": "-0 (Frontal Lobe <fMRI># Bilateral Frontal Affectation preserved consciousness) + -0 (Frontal Lobe <MRI># Bilateral Frontal Affectation preserved consciousness)",
                "Findings.Measures": "9 (structural connectivity, DTI) + 1 + 34", "Encoding Notes": "",
                "Interpretation.GNW": "X", "Interpretation.IIT": 1, "Interpretation.RPT": "X", "Interpretation.HOT": 0,
                "Affiliation": "X", "Theory Driven": "1 (HOT)",
                "Internal Replication [0 = Not, 1=Internal Replication]": 0.0, "Findings.Spatial AAL Mapping": ""}

        try:
            process_row(item=item)
        except Exception:
            raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_hidden_characters(self):
        item: dict[str | Any, str | int | Any] = {
            'Paper.Title': 'Combined behavioral and electrophysiological evidence for a direct cortical effect of prefrontal tDCS on disorders of consciousness',
            'Paper.DOI': '10.1038/s41598-020-61180-2', '# Exp': 1,
            'Experimental paradigms.Main Paradigm': 'Direct Stimulation + Disorders of Consciousness',
            'Experimental paradigms.Specific Paradigm': 'Spinal Cord Stimulation (Direct Stimulation, Spinal Cord) + Unresponsive Wakefulness Syndrome (Disorders of Consciousness) + Minimal Consciousness State (Disorders of Consciousness)',
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
            'Findings.NCC Tags': '28(Power 4-8Hz) + 14(Power 8-12Hz#parietal) + 6(PeEn #Theta-Alpha parietal) + 41(parieto-occipital, 4-10Hz) + 28(Connectivity 4-8Hz) + 14(Connectivity 8-10Hz) + 3 (52-312ms#P3a peaked at 200ms, posterior) + 3(68-392ms# P3a peaked at 200ms, left-lateralized anterior)',
            'Findings.Measures': '2 (induced # power) +9(functional, SMI) + 14(PeEn) + 3 (cluster) + 0 (MVPA)',
            'Encoding Notes': '', 'Interpretation.GNW': 1, 'Interpretation.IIT': 'X', 'Interpretation.RPT': 'X',
            'Interpretation.HOT': 'X', 'Affiliation': 'X', 'Theory Driven': '2 (GNW)',
            'Internal Replication [0 = Not, 1=Internal Replication]': 0.0, 'Findings.Spatial AAL Mapping': ''}

        self.given_studies_exist(test_file_path,
                                 sheet_name='test_studies')
        try:
            process_row(item=item)
        except Exception:
            raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_fronto_parietal(self):
        item = {
            "Paper.Title": "Fronto-parietal networks underlie the interaction between executive control and conscious "
                           "perception: Evidence from TMS and DWI",
            "Paper.DOI": "10.1016/j.cortex.2020.09.027", "# Exp": 1,
            "Experimental paradigms.Main Paradigm": "Direct Stimulation + Stimulus Degradation \u200e+ Cognitive Tasks",
            "Experimental paradigms.Specific Paradigm": "TMS (Direct Stimulation, SMA) + Contrast Reduction (Stimulus Degradation) + Executive Control (Cognitive Tasks)",
            "Experimental paradigms.Report": 1, "Sample.Type": 0, "Sample.Total": 24, "Sample.Included": 24,
            "Task.Description": "Participants were presented with a color word and a Gabor stimulus (except for catch trials, in which the Gabor was not presented). First, they had to discriminate the color of the word as fast and accurately as possible. Participants responded to this task orally RT collected through the microphone. For the computation of the accuracy, the experimenter recorded the participant\u2019s responses using four keys of the keyboard. Second, they had to report if they consciously detected the appearance of the Gabor. By choosing one of the two arrow-like stimuli (>>> or <<<) pointing to the two possible locations of target appearance. On each trial, a burst of three TMS pulses were applied at 40 Hz simultaneously to the presentation of the Stroop word and with a total duration of 56 ms. using a 70mm figure eight coil at ~45_x0003_ respect to the scalp using a a TMS neuronavigation system.",
            "Task.Code": "1 + 2", "Should be included?": 1,
            "Stimuli Features.Categories": "Words + Color + Gratings (Gabor)",
            "Stimuli Features.Description": "Colored color words (stroop task) + Gabor with a max & min contrast of .92 to .02.",
            "Stimuli Features.Modality": "Visual + Visual + Visual",
            "Stimuli Features.Duration": "515ms + 515ms + 33ms",
            "Stimuli Features.Contrast": "Gabor contrast was manipulated before the\n  experimental task in order to adjust the percentage of consciously perceived targets to ~50% (see Procedure).",
            "Measures of consciousness.Phase": "Trial By Trial", "Measures of consciousness.Type": "Objective",
            "Measures of consciousness.Description": "Accuracy in Gabor detected in congruent vs incongruent trials of stroop task. Pre experimental procidure was condacted to achieve 50% detection",
            "State - Content": 1.0, "Techniques": "MRI+\n  TMS",
            "Findings.Summary": "Gabor detection, sensitivty was enhanced for congruent trails, comparied to incongruent. Lower mean HMOA of the rSLF III -> larger TMS over rSMA effects both in perceptual sensitivity and response criterion in incongruent Stroop. Low integrity values of the left FAT -> larger TMS over rSMA effects in conscious perception for incongruent Stroop trials. integretity of SPL-SMA complex of the SFL I is a predictor for SMA-TMS effects of response creterion.",
            "Findings.NCC Tags": "9(lower integretity/valume of rSLFII, larger TMS over SMA effect # in perceptual sensitivity and response criterion incongruent Stroop trials) + 80(frontal, lower integrity of lFAT, larger TMS-SMA effect # in concious perception for incongruent Stroop trials) + 9( integretity of SPL-SMA complex of the SFL I, predictor of SMA-TMS effect #in response creterion. )",
            "Findings.Measures": "9(DWI)+52(acuracy)", "Encoding Notes": "", "Interpretation.GNW": 1,
            "Interpretation.IIT": "X", "Interpretation.RPT": "X", "Interpretation.HOT": "X", "Affiliation": "X",
            "Theory Driven": "1(GNW)", "Internal Replication [0 = Not, 1=Internal Replication]": "",
            "Findings.Spatial AAL Mapping": ""}
        self.given_studies_exist(test_file_path,
                                 sheet_name='test_studies')
        try:
            process_row(item=item)
        except Exception:
            raise AssertionError()


    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_mulitple_main_paradigms(self):
        item = {
            "Paper.Title": "Fronto-parietal networks underlie the interaction between executive control and conscious perception: Evidence from TMS and DWI",
            "Paper.DOI": "10.1016/j.cortex.2020.09.027", "# Exp": 1,
            "Experimental paradigms.Main Paradigm": "Figure-Ground + Direct Stimulation",
            "Experimental paradigms.Specific Paradigm": "TMS (Direct Stimulation, V1/V2)",
            "Experimental paradigms.Report": 1, "Sample.Type": 0, "Sample.Total": 24, "Sample.Included": 24,
            "Task.Description": "Participants were presented with a color word and a Gabor stimulus",
            "Task.Code": "1 + 2", "Should be included?": 1,
            "Stimuli Features.Categories": "Words + Color + Gratings (Gabor)",
            "Stimuli Features.Description": "Colored color words (stroop task)",
            "Stimuli Features.Modality": "Visual + Visual + Visual",
            "Stimuli Features.Duration": "515ms + 515ms + 33ms",
            "Stimuli Features.Contrast": "Gabor contrast was manipulated",
            "Measures of consciousness.Phase": "Trial By Trial", "Measures of consciousness.Type": "Objective",
            "Measures of consciousness.Description": "Accuracy in Gabor detected",
            "State - Content": 1, "Techniques": "MRI + TMS",
            "Findings.Summary": "Gabor detection",
            "Findings.NCC Tags": "9(lower integretity/valume of rSLFII, larger TMS over SMA effect # in perceptual sensitivity)",
            "Findings.Measures": "9(DWI)+52(acuracy)", "Encoding Notes": "", "Interpretation.GNW": 1,
            "Interpretation.IIT": "X", "Interpretation.RPT": "X", "Interpretation.HOT": "X", "Affiliation": "X",
            "Theory Driven": "1(GNW)", "Internal Replication [0 = Not, 1=Internal Replication]": "",
            "Findings.Spatial AAL Mapping": ""}
        self.given_studies_exist(test_file_path,
                                 sheet_name='test_studies')
        try:
            process_row(item=item)
        except Exception:
            raise AssertionError()
    def given_studies_exist(self, path, sheet_name):
        test_studies = get_list_from_excel(path, sheet_name)
        studies_data = []
        for study_item in test_studies:
            try:
                study = create_study(item=study_item)
                studies_data.append(study)
            except Exception:
                print(json.dumps(study_item))
                raise AssertionError()

        return studies_data
