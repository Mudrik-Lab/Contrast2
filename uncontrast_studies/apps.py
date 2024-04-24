from django.apps import AppConfig
from django.db.models.signals import post_save


def set_experiment_significance_via_direct_create(sender, instance, created, **kwargs):
    # Imported here because else it would run before the models are ready
    instance.experiment.calculate_significance()


class UncontrastStudiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "uncontrast_studies"

    def ready(self):
        from uncontrast_studies.models import UnConFinding

        post_save.connect(receiver=set_experiment_significance_via_direct_create, sender=UnConFinding)
