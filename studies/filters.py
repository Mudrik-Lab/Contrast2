from django_filters import rest_framework as filters

from contrast_api.choices import ReportingChoices, TypeOfConsciousnessChoices, TheoryDrivenChoices
from contrast_api.filters import BothSupportingChoiceFilter, include_either_choices, ChoicesSupportingEitherFilter
from studies.models import Experiment


class ExperimentFilter(filters.FilterSet):
    is_reporting = BothSupportingChoiceFilter(
        field_name="is_reporting", choices=include_either_choices(ReportingChoices.choices), empty_label="either"
    )
    type_of_consciousness = BothSupportingChoiceFilter(
        field_name="type_of_consciousness",
        choices=include_either_choices(TypeOfConsciousnessChoices.choices),
        empty_label="either",
    )
    theory_driven = ChoicesSupportingEitherFilter(
        field_name="theory_driven",
        choices=include_either_choices(TheoryDrivenChoices.choices),
    )

    class Meta:
        model = Experiment
        fields = ("is_reporting", "theory_driven", "type_of_consciousness")
