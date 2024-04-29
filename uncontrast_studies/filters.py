from django_filters import rest_framework as filters

from contrast_api.choices import SignificanceChoices
from contrast_api.filters import include_either_choices, ChoicesSupportingEitherFilter
from uncontrast_studies.models import UnConExperiment


class UnConExperimentFilter(filters.FilterSet):
    significance = ChoicesSupportingEitherFilter(
        field_name="significance",
        choices=include_either_choices(SignificanceChoices.choices),
    )

    class Meta:
        model = UnConExperiment
        fields = ("significance",)
