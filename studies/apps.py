from django.apps import AppConfig
from django.db.models.signals import post_save


def setup_aggregated_interpretations(sender, instance, created, **kwargs):
    # Imported here because else it would run before the models are ready
    from studies.models import AggregatedInterpretation

    AggregatedInterpretation.setup_aggregate_interpretations(instance.experiment_id)


class StudiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studies'

    def ready(self):
        from studies.models import Interpretation
        post_save.connect(receiver=setup_aggregated_interpretations, sender=Interpretation)
