from django_filters import rest_framework as filters
import django_filters

from studies.choices import ReportingChoices, TypeOfConsciousnessChoices, TheoryDrivenChoices
from studies.models import Experiment


class BothSupportingChoiceFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        self.both_value = kwargs.get("both_value", "both")

        super().__init__(*args, **kwargs)
        self.lookup_expr = "in"

    def filter(self, qs, value):
        if value is None or value == "" or (isinstance(value, str) and value.lower() == "either"):
            return qs

        fields_values = [value, self.both_value]
        qs = self.get_method(qs)(**{"%s__%s" % (self.field_name, self.lookup_expr): fields_values})
        return qs.distinct() if self.distinct else qs


def include_either_choices(choices):
    return choices + [("either", "Either")]


class ChoicesSupportingEitherFilter(django_filters.ChoiceFilter):
    def filter(self, qs, value):
        if value.lower() == "either":
            return qs

        if value != self.null_value:
            return super().filter(qs, value)

        qs = self.get_method(qs)(**{"%s__%s" % (self.field_name, self.lookup_expr): None})
        return qs.distinct() if self.distinct else qs


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
