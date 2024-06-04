from rest_framework import serializers


class NoteUpdateSerializer(serializers.Serializer):
    note = serializers.CharField()


class BooleanFlagUpdateSerializer(serializers.Serializer):
    flag = serializers.BooleanField()


class OptionalNoteUpdateSerializer(serializers.Serializer):
    note = serializers.CharField(trim_whitespace=True, allow_blank=True, allow_null=True)


class YearlySeriesSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    value = serializers.IntegerField()


class TrendsOverYearsGraphSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    series = YearlySeriesSerializer(many=True)


class HistogramSerializer(serializers.Serializer):
    key = serializers.DecimalField(max_digits=10, decimal_places=2)
    value = serializers.IntegerField()


class HistogramsGraphSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    series = HistogramSerializer(many=True)


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
