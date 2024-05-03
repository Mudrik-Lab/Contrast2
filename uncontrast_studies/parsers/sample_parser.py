from collections import namedtuple

from contrast_api.choices import UnConSampleChoices
from contrast_api.data_migration_functionality.errors import SampleTypeError, SampleSizeError, IncoherentSampleDataError


def resolve_uncon_samples(item: dict, index: str):
    samples_list = []
    resolved_sample_types = []
    resolved_sample_total_size = []
    resolved_sample_included_size = []
    resolved_sample_excluded_size = []
    samples_type_data = str(item["Samples Type"]).split(";")
    samples_total_data = str(item["Samples Total"]).split(";")
    samples_included_data = str(item["Samples Included"]).split(";")
    samples_excluded_data = str(item["Samples Excluded"]).split(";")

    for sample_type in samples_type_data:
        if sample_type.strip().lower() == "healthy adults":
            resolved_sample_type = UnConSampleChoices.HEALTHY_ADULTS
        elif sample_type.strip().lower() == "healthy college students":
            resolved_sample_type = UnConSampleChoices.HEALTHY_COLLEGE_STUDENTS
        elif sample_type.strip().lower() == "children":
            resolved_sample_type = UnConSampleChoices.CHILDREN
        elif sample_type.strip().lower() == "patients adults":
            resolved_sample_type = UnConSampleChoices.PATIENTS_ADULTS
        elif sample_type.strip().lower() == "patients children":
            resolved_sample_type = UnConSampleChoices.PATIENTS_CHILDREN
        elif sample_type.strip().lower() == "non human":
            resolved_sample_type = UnConSampleChoices.NON_HUMAN
        elif sample_type.strip().lower() == "computer":
            resolved_sample_type = UnConSampleChoices.COMPUTER
        else:
            raise SampleTypeError(f"invalid sample type {sample_type}, index {index}")
        resolved_sample_types.append(resolved_sample_type)

    for total_size in samples_total_data:
        try:
            resolved_total_size = int(total_size)
            resolved_sample_total_size.append(resolved_total_size)
        except TypeError:
            raise SampleSizeError(f"invalid sample size {total_size}, index {index}")

    for included_size in samples_included_data:
        try:
            resolved_included_size = int(included_size)
            resolved_sample_included_size.append(resolved_included_size)
        except TypeError:
            raise SampleSizeError(f"invalid sample size {included_size}, index {index}")

    for excluded_size in samples_excluded_data:
        try:
            resolved_excluded_size = int(excluded_size)
            resolved_sample_excluded_size.append(resolved_excluded_size)
        except TypeError:
            raise SampleSizeError(f"invalid sample size {excluded_size}, index {index}")

    if len(samples_type_data) == len(samples_total_data) == len(samples_included_data) == len(samples_excluded_data):
        for idx in range(len(resolved_sample_types)):
            if samples_excluded_data[idx] == 0:
                sample = UnConResolvedSample(sample_type=resolved_sample_types[idx], total_size=samples_total_data[idx],
                                             included_size=samples_included_data[idx], excluded_size=None)
                samples_list.append(sample)
            else:
                sample = UnConResolvedSample(sample_type=resolved_sample_types[idx], total_size=samples_total_data[idx],
                                             included_size=samples_included_data[idx],
                                             excluded_size=samples_excluded_data[idx])
                samples_list.append(sample)

    else:
        raise IncoherentSampleDataError(f"incoherent sample data, index {index}")

    return samples_list


UnConResolvedSample = namedtuple("UnConResolvedSample", ["sample_type", "total_size", "included_size",
                                                         "excluded_size"])
