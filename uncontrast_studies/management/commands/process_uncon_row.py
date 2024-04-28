from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist

from contrast_api.choices import ExperimentTypeChoices
from contrast_api.data_migration_functionality.studies_parsing_helpers import ProblemInStudyExistingDataException
from studies.models import Study
from uncontrast_studies.models import UnConExperiment, UnConSpecificParadigm
from uncontrast_studies.parsers.uncon_data_parsers import resolve_uncon_paradigm, resolve_uncon_stimuli_metadata

ExperimentDuplicate = namedtuple("ExperimentDuplicateTuple", ["key", "id"])


def create_uncon_experiment(item: dict, index):
    try:
        if item["Paper.DOI"]:
            study = Study.objects.get(DOI=item["Paper.DOI"])
        else:
            study = Study.objects.get(DOI=item["StudyID"])  # TODO: change back to DOI
    except ObjectDoesNotExist:
        raise ProblemInStudyExistingDataException()

    paradigm_data = resolve_uncon_paradigm(item)
    paradigm, created = UnConSpecificParadigm.objects.get_or_create(
        main=paradigm_data.main, name=paradigm_data.specific
    )
    stimuli_metadata = resolve_uncon_stimuli_metadata(item, index)

    experiment, created = UnConExperiment.objects.get_or_create(
        study=study,
        type=ExperimentTypeChoices.BEHAVIORAL,
        paradigm=paradigm,
        is_target_stimulus=stimuli_metadata.is_target_stimulus,
        is_target_same_as_suppressed_stimulus=stimuli_metadata.is_target_same_as_prime,
    )

    return experiment


def process_uncon_row(item: dict, duplicated_experiments: dict):
    # first we check for pre-existing experiment data, creating new experiment if non-existing, else fetching existing data
    study_id = item["StudyID"]
    experiment_index = item["exp"]
    composit_experiment_index = f"{study_id}, {experiment_index}"

    if composit_experiment_index not in duplicated_experiments.keys():
        experiment = create_uncon_experiment(item, composit_experiment_index)
        duplicated_experiment = ExperimentDuplicate(key=composit_experiment_index, id=experiment.id)
    else:
        duplicated_experiment = None
        experiment_id = duplicated_experiments[composit_experiment_index]
        experiment = UnConExperiment.objects.get(id=experiment_id)

    # creating non-duplicated data...

    return duplicated_experiment
