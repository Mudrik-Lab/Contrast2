from django.db import models, transaction
from django.db.models import CASCADE

from studies.choices import AggregatedInterpretationsChoices
from studies.services.aggregated_Interpretations_svc import AggregatedInterpretationService, AggregatedInterpretationDTO


class AggregatedInterpretation(models.Model):
    experiment = models.ForeignKey(to="studies.Experiment", on_delete=CASCADE, related_name="aggregated_theories")
    parent_theory_names = models.CharField(max_length=200, null=False, blank=False)
    type = models.CharField(null=False, blank=False, choices=AggregatedInterpretationsChoices.choices, max_length=30)

    def __str__(self):
        return f"experiment: {self.experiment_id} theory {self.parent_theory_names}, type {self.type}"

    @staticmethod
    @transaction.atomic
    def setup_aggregate_interpretations(experiment_id):
        from studies.models import Interpretation
        current_interpretations = Interpretation.objects.filter(experiment_id=experiment_id).select_related()
        serialized_interpretations = [AggregatedInterpretationDTO(parent_theory_names=item.theory.parent.name, type=item.type) for item in current_interpretations]
        service = AggregatedInterpretationService(serialized_interpretations)
        updated_aggregated_interpretations = service.resolve()
        # remove current ones. any way, because there might not be new ones and it's ok
        AggregatedInterpretation.objects.filter(experiment_id=experiment_id).delete()
        for aggregated_interpretation in updated_aggregated_interpretations:
            AggregatedInterpretation.objects.create(experiment_id=experiment_id,
                                                    type=aggregated_interpretation.type,
                                                    parent_theory_names=aggregated_interpretation.parent_theory_names)
