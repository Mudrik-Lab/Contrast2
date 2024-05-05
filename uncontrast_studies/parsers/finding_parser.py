from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_finding_outcomes
from contrast_api.data_migration_functionality.errors import FindingError
from uncontrast_studies.parsers.uncon_data_parsers import clean_list_from_data


def resolve_uncon_findings(item: dict, index: str):
    NULL_VALUES = ["", "NA", "N/A", "n/a", "missing"]

    resolved_findings = []
    resolved_outcome_data = []
    outcome_data = clean_list_from_data(item["Experiment's Findings Outcome"])
    significance_data = clean_list_from_data(item["Experiment's Findings Is the effect significant?"])
    number_of_trials_data = clean_list_from_data(item["Experiment's Findings Number of trials"], integer=True)
    importance_data = clean_list_from_data(item["Experiment's Findings is_important"])
    notes = []

    if len(outcome_data) == len(significance_data) == len(number_of_trials_data) == len(importance_data):
        for idx in range(len(outcome_data)):
            row_outcome = outcome_data[idx]
            row_significance = significance_data[idx]
            row_number_of_trials = number_of_trials_data[idx]
            row_importance = importance_data[idx]

            if "(" in row_outcome:
                split_outcome_data = row_outcome.split("(")
                outcome = split_outcome_data[0].strip()
                outcome_notes = split_outcome_data[1].split(")")[0].strip()
            else:
                outcome = row_outcome
                outcome_notes = None

            if outcome not in uncon_finding_outcomes:
                raise FindingError(f"invalid outcome {outcome}, exp {index}, idx {idx}")
            else:
                resolved_outcome_data.append(outcome)
                notes.append({"index": idx, "note": outcome_notes})

            if row_significance.lower() == "yes":
                is_significant = True
            elif (
                row_significance.lower() == "no" or row_significance.lower() == "missing"
            ):  # TODO: change later when no missing data
                is_significant = False
            else:
                raise FindingError(f"invalid significance {row_significance}, exp {index}, idx {idx}")

            try:
                if row_number_of_trials in NULL_VALUES:
                    number_of_trials = 1
                else:
                    number_of_trials = int(row_number_of_trials)
            except TypeError:
                raise FindingError(f"invalid number of trials {row_number_of_trials}, exp {index}, idx {idx}")

            if row_importance.lower() == "yes":
                is_important = True
            elif (
                row_importance.lower() == "no" or row_importance.lower() == "missing"
            ):  # TODO: change later when no missing data
                is_important = False
            else:
                raise FindingError(f"invalid importance {row_importance}, exp {index}, idx {idx}")

            note_data = None
            for note in notes:
                if note["index"] == idx:
                    note_data = note["note"]
                else:
                    continue

            resolved_findings.append(
                UnConResolvedFinding(
                    outcome=resolved_outcome_data[idx],
                    is_significant=is_significant,
                    is_important=is_important,
                    number_of_trials=number_of_trials,
                    notes=note_data,
                )
            )
    else:
        raise FindingError(f"incoherent number of findings for exp #{index}")

    return resolved_findings


UnConResolvedFinding = namedtuple(
    "UnConResolvedFinding", ["outcome", "is_significant", "is_important", "number_of_trials", "notes"]
)
