from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_finding_outcomes
from contrast_api.data_migration_functionality.errors import FindingError


def resolve_uncon_findings(item: dict, index: str):
    NULL_VALUES = ["", "NA", "N/A", "n/a", "missing"]
    # TODO: change to multiple findings per experiment
    resolved_findings = []
    outcome_data = str(item["Experiment's Findings Outcome"])
    significance_data = str(item["Experiment's Findings Is the effect significant?"])
    number_of_trials_data = item["Experiment's Findings Number of trials"]

    if "(" in outcome_data:
        split_outcome_data = outcome_data.split("(")
        outcome = split_outcome_data[0].strip()
        outcome_notes = split_outcome_data[1].split(")")[0].strip()
    else:
        outcome = outcome_data.strip()
        outcome_notes = None
    if outcome not in uncon_finding_outcomes:
        raise FindingError(f"invalid outcome {outcome}, index {index}")
    else:
        resolved_outcome = outcome

    if significance_data.strip().lower() == "yes":
        is_significant = True
    elif significance_data.strip().lower() == "no":
        is_significant = False
    else:
        raise FindingError(f"invalid significance {significance_data}, index {index}")

    try:
        if number_of_trials_data in NULL_VALUES:
            number_of_trials = 1
        else:
            number_of_trials = int(number_of_trials_data)
    except TypeError:
        raise FindingError(f"invalid number of trials {number_of_trials_data}, index {index}")

    resolved_findings.append(
        UnConResolvedFinding(outcome=resolved_outcome, is_significant=is_significant, is_important=True,
                             number_of_trials=number_of_trials, notes=outcome_notes))
    return resolved_findings


UnConResolvedFinding = namedtuple("UnConResolvedFinding", ["outcome", "is_significant", "is_important",
                                                           "number_of_trials", "notes"])
