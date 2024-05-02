from typing import Optional, List, Dict, Any

from contrast_api.choices import ExperimentTypeChoices
from contrast_api.tests.base import BaseTestCase
from studies.models import Study
from uncontrast_studies.models import (
    UnConSpecificParadigm,
    UnConExperiment,
    UnConFinding,
    UnConSample,
    UnConsciousnessMeasure,
    UnConProcessingDomain,
    UnConSuppressionMethod,
    UnConSuppressionMethodSubType,
    UnConSuppressionMethodType,
    UnConProcessingMainDomain,
    UnConMainParadigm,
    UnConTask,
    UnConTaskType,
    UnConSuppressedStimulus,
    UnConTargetStimulus,
    UnConModalityType,
    UnConStimulusCategory,
    UnConsciousnessMeasurePhase,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasureSubType,
)


class UnContrastBaseTestCase(BaseTestCase):
    def given_uncon_experiment_exists_for_study(
        self,
        study: Study,
        paradigm: UnConSpecificParadigm,
        findings: Optional[List[Dict[str, Any]]] = None,
        unconsciousness_measures: Optional[List[Dict[str, Any]]] = None,
        samples: Optional[List[Dict[str, Any]]] = None,
        processing_domains: Optional[List[Dict[str, Any]]] = None,
        suppression_methods: Optional[List[Dict[str, Any]]] = None,
        tasks: Optional[List[Dict[str, Any]]] = None,
        suppressed_stimuli: Optional[List[Dict[str, Any]]] = None,
        target_stimuli: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> UnConExperiment:
        default_experiment = dict(
            study=study,
            paradigm=paradigm,
            experiment_findings_notes="look what we found",
            type=ExperimentTypeChoices.BEHAVIORAL,
        )

        experiment_params = {**default_experiment, **kwargs}
        experiment, created = UnConExperiment.objects.get_or_create(**experiment_params)

        if findings:
            for item in findings:
                finding = UnConFinding.objects.create(**dict(experiment=experiment, **item))
                experiment.findings.add(finding)

        if samples:
            for item in samples:
                sample = UnConSample.objects.create(**dict(experiment=experiment, **item))
                experiment.samples.add(sample)

        if unconsciousness_measures:
            for item in unconsciousness_measures:
                unconsciousness_measure = UnConsciousnessMeasure.objects.create(**dict(experiment=experiment, **item))
                experiment.unconsciousness_measures.add(unconsciousness_measure)

        if processing_domains:
            for item in processing_domains:
                processing_domain = UnConProcessingDomain.objects.create(**dict(experiment=experiment, **item))
                experiment.processing_domains.add(processing_domain)

        if suppression_methods:
            for item in suppression_methods:
                suppression_method = UnConSuppressionMethod.objects.create(**dict(experiment=experiment, **item))
                experiment.suppression_methods.add(suppression_method)

        if tasks:
            for item in tasks:
                task = UnConTask.objects.create(**dict(experiment=experiment, **item))
                experiment.tasks.add(task)

        if suppressed_stimuli:
            for item in suppressed_stimuli:
                suppressed_stimulus = UnConSuppressedStimulus.objects.create(**dict(experiment=experiment, **item))
                experiment.suppressed_stimuli.add(suppressed_stimulus)

        if target_stimuli:
            for item in target_stimuli:
                target_stimulus = UnConTargetStimulus.objects.create(**dict(experiment=experiment, **item))
                experiment.target_stimuli.add(target_stimulus)

        return experiment

    def given_uncon_main_paradigm_exists(self, name: str):
        params = dict(
            name=name,
        )
        paradigm, created = UnConMainParadigm.objects.get_or_create(**params)
        return paradigm

    def given_uncon_stimulus_modality_type_exists(self, name: str):
        params = dict(
            name=name,
        )
        modality_type, created = UnConModalityType.objects.get_or_create(**params)
        return modality_type

    def given_uncon_stimulus_category_type_exists(self, name: str):
        params = dict(
            name=name,
        )
        category_type, created = UnConStimulusCategory.objects.get_or_create(**params)
        return category_type

    def given_unconsciousness_measure_phase_exists(self, name: str):
        params = dict(
            name=name,
        )
        un_consciousness_phase, created = UnConsciousnessMeasurePhase.objects.get_or_create(**params)
        return un_consciousness_phase  #

    def given_unconsciousness_measure_category_type_exists(self, name: str):
        params = dict(
            name=name,
        )
        un_consciousness_category_type, created = UnConsciousnessMeasureType.objects.get_or_create(**params)
        return un_consciousness_category_type

    def given_unconsciousness_measure_category_sub_type_exists(
        self, name: str, category_type: UnConsciousnessMeasureType
    ):
        params = dict(name=name, type=category_type)
        un_consciousness_category_sub_type, created = UnConsciousnessMeasureSubType.objects.get_or_create(**params)
        return un_consciousness_category_sub_type

    def given_uncon_processing_main_domain_exists(self, name: str):
        params = dict(
            name=name,
        )
        processing_main_domain, created = UnConProcessingMainDomain.objects.get_or_create(**params)
        return processing_main_domain

    def given_uncon_suppression_method_type_exists(self, name: str):
        params = dict(
            name=name,
        )
        suppression_method_type, created = UnConSuppressionMethodType.objects.get_or_create(**params)
        return suppression_method_type

    def given_uncon_suppression_method_sub_type_exists(self, name: str, parent: UnConSuppressionMethodType):
        params = dict(name=name, parent=parent)
        suppression_method_sub_type, created = UnConSuppressionMethodSubType.objects.get_or_create(**params)
        return suppression_method_sub_type

    def given_uncon_specific_paradigm_exists(self, name: str, main: Optional[UnConMainParadigm] = None):
        params = dict(name=name, main=main)
        paradigm, created = UnConSpecificParadigm.objects.get_or_create(**params)
        return paradigm
