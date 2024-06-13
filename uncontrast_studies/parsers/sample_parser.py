from collections import namedtuple

from contrast_api.choices import UnConSampleChoices
from contrast_api.data_migration_functionality.errors import SampleTypeError, SampleSizeError

UnConResolvedSample = namedtuple("UnConResolvedSample", ["sample_type", "total_size", "included_size", "excluded_size"])


def resolve_uncon_sample(item: dict, index: str):
    sample_type_data = str(item["Samples Type"]).strip()
    samples_total_data = item["Samples Total"]
    samples_included_data = item["Samples Included"]
    samples_excluded_data = item["Samples If excluded, how many?"]
    resolved_excluded_size = 0

    if sample_type_data.lower() == "healthy adults":
        resolved_sample_type = UnConSampleChoices.HEALTHY_ADULTS
    elif sample_type_data.lower() == "healthy college students":
        resolved_sample_type = UnConSampleChoices.HEALTHY_COLLEGE_STUDENTS
    elif sample_type_data.lower() == "children":
        resolved_sample_type = UnConSampleChoices.CHILDREN
    elif sample_type_data.lower() == "patients adults":
        resolved_sample_type = UnConSampleChoices.PATIENTS_ADULTS
    elif sample_type_data.lower() == "patients children":
        resolved_sample_type = UnConSampleChoices.PATIENTS_CHILDREN
    elif sample_type_data.lower() == "non human":
        resolved_sample_type = UnConSampleChoices.NON_HUMAN
    elif sample_type_data.lower() == "computer":
        resolved_sample_type = UnConSampleChoices.COMPUTER
    else:
        raise SampleTypeError(f"invalid sample type {sample_type_data}, index {index}")

    try:
        resolved_total_size = int(samples_total_data)
    except (TypeError, ValueError):
        raise SampleSizeError(f"invalid sample size {samples_total_data}, index {index}")

    try:
        resolved_included_size = int(samples_included_data)
    except (TypeError, ValueError):
        raise SampleSizeError(f"invalid sample size {samples_included_data}, index {index}")

    if samples_excluded_data == "missing":
        resolved_excluded_size = 0
    else:
        try:
            resolved_excluded_size = int(samples_excluded_data)
        except (TypeError, ValueError):
            raise SampleSizeError(f"invalid sample size {samples_excluded_data}, index {index}")

    sample = UnConResolvedSample(
        sample_type=resolved_sample_type,
        total_size=resolved_total_size,
        included_size=resolved_included_size,
        excluded_size=resolved_excluded_size,
    )

    return sample
