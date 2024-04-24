# TODO custom experiment manager with all the select_related for the joins
# Probably needs a custom queryset
from django.db import models
from django.db.models import Prefetch


class UnConExperimentManager(models.Manager):
    def related(self):
        from uncontrast_studies.models import (
            UnConTask,
            UnConsciousnessMeasure,
            UnConSuppressedStimulus,
            UnConTargetStimulus,
            UnConFinding,
            UnConProcessingDomain,
            UnConSuppressionMethod,
        )

        return (
            self.get_queryset()
            .select_related("study", "paradigm")
            .prefetch_related("study__authors")
            .prefetch_related(Prefetch("tasks", queryset=UnConTask.objects.select_related("type")))
            .prefetch_related(Prefetch("findings", queryset=UnConFinding.objects))
            .prefetch_related(
                Prefetch(
                    "consciousness_measures", queryset=UnConsciousnessMeasure.objects.select_related("type", "phase")
                )
            )
            .prefetch_related(
                Prefetch(
                    "suppressed_stimuli",
                    queryset=UnConSuppressedStimulus.objects.select_related("category", "sub_category", "modality"),
                ),
            )
            .prefetch_related(
                Prefetch(
                    "target_stimuli",
                    queryset=UnConTargetStimulus.objects.select_related("category", "sub_category", "modality"),
                )
            )
            .prefetch_related("samples")
            .prefetch_related(
                Prefetch(
                    "suppression_methods", queryset=UnConSuppressionMethod.objects.select_related("type", "sub_type")
                )
            )
            .prefetch_related(
                Prefetch(
                    "processing_domains", queryset=UnConProcessingDomain.objects.select_related("main", "sub_domain")
                )
            )
        )
