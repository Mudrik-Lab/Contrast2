from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import NumericRangeFilter

from studies.admin import BaseContrastAdmin
from uncontrast_studies.models import (
    UnConsciousnessMeasure,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasurePhase,
    UnConsciousnessMeasureSubType,
    UnConSuppressedStimulus,
    UnConStimulusSubCategory,
    UnConStimulusCategory,
    UnConModalityType,
    UnConTaskType,
    UnConTask,
    UnConTargetStimulus,
    UnConMainParadigm,
    UnConSpecificParadigm,
    UnConSample,
    UnConProcessingMainDomain,
    UnConProcessingDomain,
    UnConSuppressionMethod,
    UnConSuppressionMethodType,
    UnConSuppressionMethodSubType,
    UnConExperiment,
)


class UnConExperimentAdmin(BaseContrastAdmin):
    model = UnConExperiment
    list_display = ("id", "significance")
    list_filter = ("significance",)


class UnConsciousnessMeasureAdmin(BaseContrastAdmin):
    list_display = (
        "phase",
        "type",
        "sub_type",
        "number_of_trials",
        "number_of_participants_in_awareness_test",
        "is_trial_excluded_based_on_measure",
        "experiment_id",
    )
    model = UnConsciousnessMeasure
    list_filter = (
        "is_cm_same_participants_as_task",
        "is_performance_above_chance",
        "is_trial_excluded_based_on_measure",
        ("phase", admin.RelatedOnlyFieldListFilter),
        ("type", admin.RelatedOnlyFieldListFilter),
        ("sub_type", admin.RelatedOnlyFieldListFilter),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


class UnConsciousnessMeasureTypeAdmin(ImportExportModelAdmin):
    model = UnConsciousnessMeasureType
    list_display = ("id", "name")


class UnConsciousnessMeasureSubTypeAdmin(ImportExportModelAdmin):
    model = UnConsciousnessMeasureSubType
    list_display = ("id", "name", "type")
    list_filter = (("type", admin.RelatedOnlyFieldListFilter),)


class UnConsciousnessMeasurePhaseTypeAdmin(ImportExportModelAdmin):
    model = UnConsciousnessMeasurePhase
    list_display = ("id", "name")


class UnConModalityTypeAdmin(ImportExportModelAdmin):
    model = UnConModalityType
    list_display = ("id", "name")


class UnConStimulusCategoryAdmin(ImportExportModelAdmin):
    model = UnConStimulusCategory
    list_display = ("id", "name")
    search_fields = ("name",)


class UnConStimulusSubCategoryAdmin(ImportExportModelAdmin):
    list_display = ("id", "name", "parent")
    model = UnConStimulusSubCategory
    list_filter = ("parent",)
    search_fields = ("name",)


class UnConTargetStimulusAdmin(BaseContrastAdmin):
    list_display = ("id", "category", "sub_category", "modality", "number_of_stimuli")
    model = UnConTargetStimulus

    list_filter = (
        ("category", admin.RelatedOnlyFieldListFilter),
        ("sub_category", admin.RelatedOnlyFieldListFilter),
        ("modality", admin.RelatedOnlyFieldListFilter),
    )


class UnConSuppressedStimulusAdmin(BaseContrastAdmin):
    list_display = (
        "id",
        "category",
        "sub_category",
        "modality",
        "mode_of_presentation",
        "soa",
        "number_of_stimuli",
        "duration",
        "experiment_id",
    )
    model = UnConSuppressedStimulus
    list_filter = (
        ("category", admin.RelatedOnlyFieldListFilter),
        ("sub_category", admin.RelatedOnlyFieldListFilter),
        ("modality", admin.RelatedOnlyFieldListFilter),
    )

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("category", "sub_category", "modality", "sub_category__parent")
        )


class UnConTaskTypeAdmin(ImportExportModelAdmin):
    model = UnConTaskType
    list_display = ("id", "name")
    search_fields = ("name",)


class UnConTaskAdmin(BaseContrastAdmin):
    list_display = ("id", "type", "experiment_id")
    model = UnConTask
    list_filter = (("type", admin.RelatedOnlyFieldListFilter),)


class UnConMainParadigmAdmin(BaseContrastAdmin):
    model = UnConMainParadigm
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)


class UnConSpecificParadigmAdmin(BaseContrastAdmin):
    model = UnConSpecificParadigm
    list_display = ("id", "name")
    search_fields = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("main")


class UnConSampleAdmin(BaseContrastAdmin):
    model = UnConSample
    list_filter = (
        "type",
        ("size_excluded", NumericRangeFilter),
        ("size_included", NumericRangeFilter),
        ("size_total", NumericRangeFilter),
    )
    list_display = ("type", "size_excluded", "size_included", "size_total", "experiment_id")


class UnConProcessingDomainMainTypeAdmin(BaseContrastAdmin):
    model = UnConProcessingMainDomain
    list_display = ("id", "name")


class UnConProcessingDomainAdmin(BaseContrastAdmin):
    model = UnConProcessingDomain
    list_display = ("main", "experiment_id")


class UnConSuppressionMethodTypeAdmin(BaseContrastAdmin):
    model = UnConSuppressionMethodType
    list_display = ("id", "name")


class UnConSuppressionMethodSubTypeAdmin(BaseContrastAdmin):
    model = UnConSuppressionMethodSubType
    list_display = ("id", "name")


class UnConSuppressionMethodAdmin(BaseContrastAdmin):
    model = UnConSuppressionMethod
    list_display = ("id", "type", "sub_type")
    list_filter = (
        "type",
        "sub_type",
    )


admin.site.register(UnConsciousnessMeasure, UnConsciousnessMeasureAdmin)
admin.site.register(UnConsciousnessMeasureType, UnConsciousnessMeasureTypeAdmin)
admin.site.register(UnConsciousnessMeasureSubType, UnConsciousnessMeasureSubTypeAdmin)
admin.site.register(UnConsciousnessMeasurePhase, UnConsciousnessMeasurePhaseTypeAdmin)
admin.site.register(UnConSuppressedStimulus, UnConSuppressedStimulusAdmin)
admin.site.register(UnConTargetStimulus, UnConTargetStimulusAdmin)
admin.site.register(UnConStimulusCategory, UnConStimulusCategoryAdmin)
admin.site.register(UnConStimulusSubCategory, UnConStimulusSubCategoryAdmin)
admin.site.register(UnConModalityType, UnConModalityTypeAdmin)
admin.site.register(UnConMainParadigm, UnConMainParadigmAdmin)
admin.site.register(UnConSpecificParadigm, UnConSpecificParadigmAdmin)
admin.site.register(UnConSample, UnConSampleAdmin)
admin.site.register(UnConProcessingMainDomain, UnConProcessingDomainMainTypeAdmin)
admin.site.register(UnConProcessingDomain, UnConProcessingDomainAdmin)
admin.site.register(UnConSuppressionMethod, UnConSuppressionMethodAdmin)
admin.site.register(UnConSuppressionMethodSubType, UnConSuppressionMethodSubTypeAdmin)
admin.site.register(UnConSuppressionMethodType, UnConSuppressionMethodTypeAdmin)
admin.site.register(UnConExperiment, UnConExperimentAdmin)
