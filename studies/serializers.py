from rest_framework.serializers import ModelSerializer

from studies.models import Experiment, Study


class ExperimentSerializer(ModelSerializer):
    class Meta:
        model = Experiment
        fields = "__all__"


class StudySerializer(ModelSerializer):
    class Meta:
        model = Study
        fields = "__all__"