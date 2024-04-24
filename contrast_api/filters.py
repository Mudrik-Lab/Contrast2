import django_filters


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
