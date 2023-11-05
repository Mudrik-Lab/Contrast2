# TODO custom experiment manager with all the select_related for the joins
# Probably needs a custom queryset
from django.db import models
from django.db.models import Prefetch


class ExperimentManager(models.Manager):
    def related(self):
        from studies.models import Measure, Task, ConsciousnessMeasure, Stimulus, Paradigm, FindingTag

        return (
            self.get_queryset()
            .select_related("study")
            .prefetch_related("study__authors")
            .prefetch_related("theory_driven_theories")
            .prefetch_related("aggregated_theories")
            .prefetch_related(Prefetch("measures", queryset=Measure.objects.select_related("type")))
            .prefetch_related(Prefetch("tasks", queryset=Task.objects.select_related("type")))
            .prefetch_related(Prefetch("finding_tags", queryset=FindingTag.objects.select_related("type", "family")))
            .prefetch_related(
                Prefetch(
                    "consciousness_measures", queryset=ConsciousnessMeasure.objects.select_related("type", "phase")
                )
            )
            .prefetch_related(
                Prefetch("stimuli", queryset=Stimulus.objects.select_related("category", "sub_category", "modality"))
            )
            .prefetch_related("samples")
            .prefetch_related(
                Prefetch("paradigms", queryset=Paradigm.objects.select_related("parent", "parent__parent"))
            )
            .prefetch_related("techniques")
        )
