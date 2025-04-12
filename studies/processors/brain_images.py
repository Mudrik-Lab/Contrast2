from django.db.models import QuerySet, Count
import pandas as pd
from contrast_api.application_services.brain_images import BrainImageCreatorService
from contrast_api.choices import InterpretationsChoices
from studies.models import Theory, Experiment, FindingTag, Interpretation
from studies.processors.base import BaseProcessor
from studies.resources.finding_tag import FindingTagResource


class BrainImagesDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        self.theory = None

        theory = kwargs.pop("theory", [])
        if len(theory):
            theory_reference = theory[0]
            try:
                theory = Theory.objects.get(name__iexact=theory_reference)
            except Theory.DoesNotExist:
                theory = Theory.objects.get(id=theory_reference)
            self.theory = theory

        if self.theory:
            interpretations = Interpretation.objects.filter(type=InterpretationsChoices.PRO, theory__parent=self.theory)
            self.experiments = self.experiments.filter(id__in=interpretations.values_list("experiment_id", flat=True))
        # TODO handle "all" when we have multi brains

    def get_queryset(self):
        queryset = FindingTag.objects.annotate(tag_count=Count("AAL_atlas_tags")).filter(
            is_NCC=True,
            family__name="Spatial Areas",
            technique__name__iexact="fmri",
            tag_count__gt=0,
            experiment__in=self.experiments,
        )

        return queryset

    def process(self):
        queryset = self.get_queryset()
        if self.is_csv:
            return queryset.values_list("id", flat=True)

        # turn queryset to pandas df

        resource = FindingTagResource()  # reusing from the admin
        findings_df = resource.export(queryset=queryset).export("df")

        # TODO: later - work on multi brain
        svc = BrainImageCreatorService(findings_df=findings_df, theory=self.theory.name)
        brain_views = svc.create_brain_image()
        return [brain_views]
