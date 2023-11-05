from django.apps import AppConfig
from django.db.models.signals import post_save, m2m_changed


def setup_aggregated_interpretations_via_direct_create(sender, instance, created, **kwargs):
    # Imported here because else it would run before the models are ready
    from studies.models import AggregatedInterpretation

    AggregatedInterpretation.setup_aggregate_interpretations(instance.experiment_id)


def setup_aggregated_interpretations_via_add(sender, instance, pk_set, action, **kwargs):
    # in this case the sender can be the experiment, or the theory adding the interpretations
    if action not in ["post_add", "post_remove", "post_clear"]:
        return
    from studies.models import AggregatedInterpretation, Experiment, Theory

    if isinstance(instance, Experiment):
        AggregatedInterpretation.setup_aggregate_interpretations(instance.id)

    elif isinstance(instance, Theory):
        for pk in pk_set:
            AggregatedInterpretation.setup_aggregate_interpretations(pk)


class StudiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "studies"

    def ready(self):
        from studies.models import Interpretation

        post_save.connect(receiver=setup_aggregated_interpretations_via_direct_create, sender=Interpretation)
        m2m_changed.connect(receiver=setup_aggregated_interpretations_via_add, sender=Interpretation)
