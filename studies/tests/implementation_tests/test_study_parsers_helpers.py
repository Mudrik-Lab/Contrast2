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
    def test_Cingulate_Mid_finding(self):
        study = self.given_studies_exist('studies/data/test_data.xlsx',
                                                sheet_name='test_studies')

        item: dict[str | Any, str | int | Any] = {"Paper.Title": "Pain-Evoked Reorganization in Functional Brain Networks", "Paper.DOI": "10.1093/cercor/bhz276", "# Exp": 1, "Experimental paradigms.Main Paradigm": "Pain", "Experimental paradigms.Specific Paradigm": "Pain", "Experimental paradigms.Report": 0, "Sample.Type": 0, "Sample.Total": 119, "Sample.Included": 106, "Task.Description": "participants received a series of contact-heat stimulus using a TSA-II Neurosensory Analyzer (Medoc Ltd) with a 16mmPeltier thermode endplate (Study 7:32 mm) and rated the magnitude of pain they felt on a visual analog scale (VAS) after stimulus offset. focus was on investigating the difference between noxious and innocuous stimuli in functional network organization, and all psychological manipulations were balanced across (orthogonal to) noxious and innocuous conditions. 45.3 \u25e6C was used as a threshold for dividing thermal stimulation into innocuous (stimulation intensity <45.3 \u25e6C) and noxious (stimulation intensity >45.3 \u25e6C) conditions.", "Task.Code": 0, "Should be included?": 1, "Stimuli Features.Categories": "Nociceptive stimulation", "Stimuli Features.Description": "innocuous (stimulation intensity <45.3 \u25e6C) and noxious (stimulation intensity >45.3 \u25e6C) conditions", "Stimuli Features.Modality": "Tactile", "Stimuli Features.Duration": "", "Stimuli Features.Contrast": "None", "Measures of consciousness.Phase": "Trial By Trial", "Measures of consciousness.Type": "Objective", "Measures of consciousness.Description": "None", "State - Content": "", "Techniques": "fMRI", "Findings.Summary": "pain integrates somatosensory activity with frontoparietal systems (the CCN here). cortical targets of nociceptive afferents (generally located in SMN and ION here) and frontoparietal systems (CCN). We found that all of these systems are integrated\n  during pain.", "Findings.NCC Tags": "9(Frontal_Inf_Oper_L & Cingulate_Mid_R & Frontal_Mid_L & Frontal_Sup_L)", "Findings.Measures": "9(functional)", "Encoding Notes": "", "Interpretation.GNW": 1, "Interpretation.IIT": "X", "Interpretation.RPT": "X", "Interpretation.HOT": "X", "Affiliation": "X", "Theory Driven": 0, "Internal Replication [0 = Not, 1=Internal Replication]": "", "Findings.Spatial AAL Mapping": "Frontal_Inf_Oper_L + Cingulum_Mid_R + Frontal_Mid_L + Frontal_Sup_L"}


        try:
            process_row(item=item)
        except:
            raise AssertionError()

    @unittest.skipIf(test_data_doesnt_exist(), "Skipping if test_data doesn't exist")
    def test_spinal_cord(self):
        test_study = [{"DOI": "10.1038/s41598-020-61180-2",
                       "Title": "Combined behavioral and electrophysiological evidence for a direct cortical effect of prefrontal tDCS on disorders of consciousness",
                       "Year": 2020,
                       "Authors": "Hermann B., Raimondo F., Hirsch L., Huang Y., Denis-Valente M., P\u00e9rez P., Engemann D., Faugeras F., Weiss N., Demeret S., Rohaut B., Parra L.C., Sitt J.D., Naccache L.",
                       "Source.Title": "Scientific Reports",
                       "Affiliations": "Institut du Cerveau et de la Moelle \u00e9pini\u00e8re, ICM, Paris, F-75013, France; Inserm U 1127, Paris, F-75013, France; CNRS UMR 7225, Paris, F-75013, France; Department of Neurology, Neuro ICU, H\u00f4pital de la Piti\u00e9-Salp\u00eatri\u00e8re, AP-HP, Paris, F-75013, France; Laboratorio de Inteligencia Artificial Aplicada, Departamento de Computaci\u00f3n FCEyN, UBA, Ciudad Aut\u00f3noma de Buenos Aires, C1428EGA, Argentina; CONICET \u2013 Universidad de Buenos Aires, Instituto de Investigaci\u00f3n en Ciencias de la Computaci\u00f3n, Godoy Cruz 2290, Ciudad Aut\u00f3noma de Buenos Aires, C1425FQB, Argentina; Biomedical Engineering Department, City College of the City University of New York, New York, NY  10031, United States; Department of Neurophysiology, H\u00f4pital de la Piti\u00e9-Salp\u00eatri\u00e8re, AP-HP, Paris, F-75013, France; Parietal project-team, INRIA, Universit\u00e9 Paris-Saclay, Saclay, 91120, France; Cognitive Neuroimaging Unit, CEA DSV/I2BM, INSERM, Universit\u00e9 Paris-Sud, Universit\u00e9 Paris-Saclay, NeuroSpin center, Gif-sur-Yvette, 91191, France; Facult\u00e9 de M\u00e9decine Piti\u00e9-Salp\u00eatri\u00e8re, Sorbonne Universit\u00e9, Paris, 75013, France; Department of Neurology, Columbia University, New York, NY  10027, United States",
                       "Abstract": "Severe brain injuries can lead to long-lasting disorders of consciousness (DoC) such as vegetative state/unresponsive wakefulness syndrome (VS/UWS) or minimally conscious state (MCS). While behavioral assessment remains the gold standard to determine conscious state, EEG has proven to be a promising complementary tool to monitor the effect of new therapeutics. Encouraging results have been obtained with invasive electrical stimulation of the brain, and recent studies identified transcranial direct current stimulation (tDCS) as an effective approach in randomized controlled trials. This non-invasive and inexpensive tool may turn out to be the preferred treatment option. However, its mechanisms of action and physiological effects on brain activity remain unclear and debated. Here, we stimulated 60 DoC patients with the anode placed over left-dorsolateral prefrontal cortex in a prospective open-label study. Clinical behavioral assessment improved in twelve patients (20%) and none deteriorated. This behavioral response after tDCS coincided with an enhancement of putative EEG markers of consciousness: in comparison with non-responders, responders showed increases of power and long-range cortico-cortical functional connectivity in the theta-alpha band, and a larger and more sustained P300 suggesting improved conscious access to auditory novelty. The EEG changes correlated with electric fields strengths in prefrontal cortices, and no correlation was found on the scalp. Taken together, this prospective intervention in a large cohort of DoC patients strengthens the validity of the proposed EEG signatures of consciousness, and is suggestive of a direct causal effect of tDCS on consciousness. \u00a9 2020, The Author(s).",
                       "Author.Keywords": "",
                       "Funding.Details": "This work was supported by: \u2018e(ye)BRAIN, Ivry-sur-Seine, France\u2019, \u2018Institut National de la Sant\u00e9 et de la Recherche M\u00e9dicale\u2019 (BH, LN, JS), Sorbonne Universit\u00e9 (LN), the James S. McDonnell Foundation (LN), FRM 2015 (LN), UNIM (LN), Acad\u00e9mie des Sciences-Lamonica Prize 2016 (LN). The research leading to these results has received funding from the program \u2018Investissements d\u2019avenir\u2019 ANR-10-IAIHU-06, \u2018and by ANR grant \u2018CogniComa\u2019 (ANR-14-CE-0013-03). BH was funded by \u2018Poste d\u2019Accueil Inserm\u2019 grant.",
                       "Abbreviated.Source.Title": "Sci. Rep."}]
        study = self.given_studies_exist(test_study)[0]

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
            'Findings.NCC Tags': '6 (PeEn # higher PeEn in frontal and centrel electrodes after SCS in MCS pre-SCS larger change after SCS compared to UWS and a positive correlation with CRS-R only in frontal electrodes) + 0 (Frontal electrodes # PeEn effects were found in frontal and central electrodes).',
            'Findings.Measures': '2 (induced # power) +9(functional, SMI) + 14(PeEn) + 3 (cluster) + 0 (MVPA)',
            'Encoding Notes': '', 'Interpretation.GNW': 1, 'Interpretation.IIT': 'X', 'Interpretation.RPT': 'X',
            'Interpretation.HOT': 'X', 'Affiliation': 'X', 'Theory Driven': '2 (GNW)',
            'Internal Replication [0 = Not, 1=Internal Replication]': 0.0, 'Findings.Spatial AAL Mapping': ''}

        try:
            process_row(item=item)
        except:
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
            'Experimental paradigms.Main Paradigm': 'Direct stimulation + Disorders of Consciousness',
            'Experimental paradigms.Specific Paradigm': 'Spinal Cord Stimulation (Direct Stimulation, Spinal Cord) + Unresponsive Wakefulness Syndrome (Disorders of Consciousness) + Minimal Consciousness State (Disorders of Consciousness)',
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

    def test_fronto_parietal(self):
        item = {"Paper.Title": "Fronto-parietal networks underlie the interaction between executive control and conscious perception: Evidence from TMS and DWI", "Paper.DOI": "10.1016/j.cortex.2020.09.027", "# Exp": 1, "Experimental paradigms.Main Paradigm": "Direct Stimulation + Stimulus Degradation \u200e+ Cognitive Tasks", "Experimental paradigms.Specific Paradigm": "TMS (Direct Stimulation, SMA) + Contrast Reduction (Stimulus Degradation) + Executive Control (Cognitive Tasks)", "Experimental paradigms.Report": 1, "Sample.Type": 0, "Sample.Total": 24, "Sample.Included": 24, "Task.Description": "Participants were presented with a color word and a Gabor stimulus (except for catch trials, in which the Gabor was not presented). First, they had to discriminate the color of the word as fast and accurately as possible. Participants responded to this task orally RT collected through the microphone. For the computation of the accuracy, the experimenter recorded the participant\u2019s responses using four keys of the keyboard. Second, they had to report if they consciously detected the appearance of the Gabor. By choosing one of the two arrow-like stimuli (>>> or <<<) pointing to the two possible locations of target appearance. On each trial, a burst of three TMS pulses were applied at 40 Hz simultaneously to the presentation of the Stroop word and with a total duration of 56 ms. using a 70mm figure eight coil at ~45_x0003_ respect to the scalp using a a TMS neuronavigation system.", "Task.Code": "1 + 2", "Should be included?": 1, "Stimuli Features.Categories": "Words + Color + Gratings (Gabor)", "Stimuli Features.Description": "Colored color words (stroop task) + Gabor with a max & min contrast of .92 to .02.", "Stimuli Features.Modality": "Visual + Visual + Visual", "Stimuli Features.Duration": "515ms + 515ms + 33ms", "Stimuli Features.Contrast": "Gabor contrast was manipulated before the\n  experimental task in order to adjust the percentage of consciously perceived targets to ~50% (see Procedure).", "Measures of consciousness.Phase": "Trial By Trial", "Measures of consciousness.Type": "Objective", "Measures of consciousness.Description": "Accuracy in Gabor detected in congruent vs incongruent trials of stroop task. Pre experimental procidure was condacted to achieve 50% detection", "State - Content": 1.0, "Techniques": "MRI+\n  TMS", "Findings.Summary": "Gabor detection, sensitivty was enhanced for congruent trails, comparied to incongruent. Lower mean HMOA of the rSLF III -> larger TMS over rSMA effects both in perceptual sensitivity and response criterion in incongruent Stroop. Low integrity values of the left FAT -> larger TMS over rSMA effects in conscious perception for incongruent Stroop trials. integretity of SPL-SMA complex of the SFL I is a predictor for SMA-TMS effects of response creterion.", "Findings.NCC Tags": "9(lower integretity/valume of rSLFII, larger TMS over SMA effect # in perceptual sensitivity and response criterion incongruent Stroop trials) + 80(frontal, lower integrity of lFAT, larger TMS-SMA effect # in concious perception for incongruent Stroop trials) + 9( integretity of SPL-SMA complex of the SFL I, predictor of SMA-TMS effect #in response creterion. )", "Findings.Measures": "9(DWI)+52(acuracy)", "Encoding Notes": "", "Interpretation.GNW": 1, "Interpretation.IIT": "X", "Interpretation.RPT": "X", "Interpretation.HOT": "X", "Affiliation": "X", "Theory Driven": "1(GNW)", "Internal Replication [0 = Not, 1=Internal Replication]": "", "Findings.Spatial AAL Mapping": ""}
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
