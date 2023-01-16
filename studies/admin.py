from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from studies.models import Study, Experiment, Author, ConsciousnessMeasure, ConsciousnessMeasureType, \
    ConsciousnessMeasurePhaseType, FindingTagFamily, FindingTagType, FindingTag, Interpretation, MeasureType, Measure, \
    Paradigm, Sample, ModalityType, TaskType, Task, Technique, Theory
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, Stimulus


# Register your models here.

class ExperimentAdmin(ImportExportModelAdmin):
    model = Experiment
    list_filter = ("type_of_consciousness", "type", "is_reporting", "theory_driven", "study__approval_status")

    def get_queryset(self, request):
        qs = super().get_queryset(request=request)
        return qs.select_related("study")


# TODO: add filters for experiment
# TODO: add relevant inlines for experiment (everything that has foreign key to it)

class ExperimentInline(admin.StackedInline):
    model = Experiment
    # fields =
    show_change_link = True
    extra = 0

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


class StudyAdmin(ImportExportModelAdmin):
    model = Study
    fields = ("id", "name")
    search_fields = ("name",)
    inlines = [
        ExperimentInline
    ]


class AuthorAdmin(ImportExportModelAdmin):
    model = Author


class ConsciousnessMeasureAdmin(ImportExportModelAdmin):
    model = ConsciousnessMeasure
    list_filter = ("phase", "type")


class ConsciousnessMeasureTypeAdmin(ImportExportModelAdmin):
    model = ConsciousnessMeasureType


class ConsciousnessMeasurePhaseTypeAdmin(ImportExportModelAdmin):
    model = ConsciousnessMeasurePhaseType


class FindingTagFamilyAdmin(ImportExportModelAdmin):
    model = FindingTagFamily


class FindingTagTypeAdmin(ImportExportModelAdmin):
    model = FindingTagType


class FindingTagAdmin(ImportExportModelAdmin):
    model = FindingTag
    list_filter = ("type", "family")


class InterpretationAdmin(ImportExportModelAdmin):
    model = Interpretation
    list_filter = ("type", "theory")


class MeasureTypeAdmin(ImportExportModelAdmin):
    model = MeasureType


class MeasureAdmin(ImportExportModelAdmin):
    model = Measure
    list_filter = ("type",)


class ParadigmAdmin(ImportExportModelAdmin):
    model = Paradigm
    list_filter = ("parent__name",)


class SampleAdmin(ImportExportModelAdmin):
    model = Sample
    list_filter = ("type",)


class ModalityTypeAdmin(ImportExportModelAdmin):
    model = ModalityType


class StimulusCategoryAdmin(ImportExportModelAdmin):
    model = StimulusCategory


class StimulusSubCategoryAdmin(ImportExportModelAdmin):
    model = StimulusSubCategory


class StimulusAdmin(ImportExportModelAdmin):
    model = Stimulus
    list_filter = ("category", "sub_category", "modality")


class TaskTypeAdmin(ImportExportModelAdmin):
    model = TaskType


class TaskAdmin(ImportExportModelAdmin):
    model = Task
    list_filter = ("type",)


class TechniqueAdmin(ImportExportModelAdmin):
    model = Technique


class TheoryAdmin(ImportExportModelAdmin):
    model = Theory


admin.site.disable_action('delete_selected')  # Site wide
admin.site.register(Study, StudyAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(ConsciousnessMeasurePhaseType, ConsciousnessMeasurePhaseTypeAdmin)
admin.site.register(ConsciousnessMeasureType, ConsciousnessMeasureTypeAdmin)
admin.site.register(ConsciousnessMeasure, ConsciousnessMeasureAdmin)
admin.site.register(FindingTagFamily, FindingTagFamilyAdmin)
admin.site.register(FindingTagType, FindingTagTypeAdmin)
admin.site.register(FindingTag, FindingTagAdmin)
admin.site.register(Interpretation, InterpretationAdmin)
admin.site.register(MeasureType, MeasureTypeAdmin)
admin.site.register(Measure, MeasureAdmin)
admin.site.register(Paradigm, ParadigmAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(Stimulus, StimulusAdmin)
admin.site.register(StimulusCategory, StimulusCategoryAdmin)
admin.site.register(StimulusSubCategory, StimulusSubCategoryAdmin)
admin.site.register(ModalityType, ModalityTypeAdmin)
admin.site.register(TaskType, TaskTypeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Technique, TechniqueAdmin)
admin.site.register(Theory, TheoryAdmin)
