from django_countries import countries
from rest_framework import serializers


class NationOfConsciousnessGraphSerializer(serializers.Serializer):
    country = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    value = serializers.IntegerField()
    total = serializers.IntegerField()
    theory = serializers.CharField(source="theory__parent__name")

    def get_country(self, obj) -> str:
        return countries.alpha3(obj["country"])

    def get_country_name(self, obj) -> str:
        return countries.name(obj["country"])


class NoteUpdateSerializer(serializers.Serializer):
    note = serializers.CharField()


class OptionalNoteUpdateSerializer(serializers.Serializer):
    note = serializers.CharField(trim_whitespace=True, allow_blank=True, allow_null=True)


class YearlySeriesSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    value = serializers.IntegerField()


class TrendsOverYearsGraphSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    series = YearlySeriesSerializer(many=True)


class BarGraphSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    key = serializers.CharField()


class StackedBarGraphSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    series = BarGraphSerializer(many=True)


class DurationBarSerializer(serializers.Serializer):
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    name = serializers.CharField()


class DurationGraphSerializer(serializers.Serializer):
    series = DurationBarSerializer(many=True)


class NestedPieChartSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    value = serializers.IntegerField()
    series = BarGraphSerializer(many=True)


class PieChartSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    value = serializers.IntegerField()
    series = BarGraphSerializer(many=True)


class ComparisonNestedPieChartSerializer(serializers.Serializer):
    theories = PieChartSerializer(many=True)
