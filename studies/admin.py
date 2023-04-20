from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _
from django_countries import countries

from studies.models import Study, Experiment, Author, ConsciousnessMeasure, ConsciousnessMeasureType, \
    ConsciousnessMeasurePhaseType, FindingTagFamily, FindingTagType, FindingTag, Interpretation, MeasureType, Measure, \
    Paradigm, Sample, ModalityType, TaskType, Task, Technique, Theory
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, Stimulus


# Register your models here.

class ExperimentAdmin(ImportExportModelAdmin):
    # todo add theory to display
    list_display = ("id", "type_of_consciousness", "is_reporting", "theory_driven", "study__title",)
    model = Experiment
    fields = ("type_of_consciousness", "is_reporting", "theory_driven", "techniques", "paradigms")
    list_filter = ("type_of_consciousness", "type", "is_reporting", "theory_driven", "study__approval_status")
    filter_horizontal = ("paradigms", "techniques")

    def get_queryset(self, request):
        qs = super().get_queryset(request=request)
        # trying to optimize this view, but alas, currently the custom Prefetch doesn't seem to be working
        return qs.select_related("study") \
            .prefetch_related(Prefetch('paradigms', queryset=Paradigm.objects.select_related('parent'))) \
            .prefetch_related("techniques")

    @admin.display(empty_value="")
    def study__title(self, obj):
        return obj.study.title


# TODO: add relevant inlines for experiment (everything that has foreign key to it)

class ExperimentInline(admin.StackedInline):
    model = Experiment
    filter_horizontal = ("techniques", "paradigms")

    # fields =
    show_change_link = True
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request=request)
        # trying to optimize this view, but alas, currently the custom Prefetch doesn't seem to be working
        return qs.select_related("study") \
            .prefetch_related(Prefetch('paradigms', queryset=Paradigm.objects.select_related('parent'))) \
            .prefetch_related("techniques")

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


class CountryFilter(admin.SimpleListFilter):
    title = 'Country'
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        # Get a list of all distinct countries that exist in the database
        existing_countries = model_admin.get_queryset(request).values_list('countries', flat=True).distinct()
        flattened_existing_countries = sorted(
            set(country for the_countries in existing_countries for country in the_countries))

        # Create a list of tuples for the filter dropdown
        # Each tuple contains the country code and name
        return [(country, countries.name(country)) for country in flattened_existing_countries]

    def queryset(self, request, queryset):
        # If a country code is selected in the filter,
        # return only the studies that have that country
        if self.value():
            return queryset.filter(countries__contains=[self.value()])


class StudyAdmin(ImportExportModelAdmin):
    model = Study
    filter_horizontal = ("authors",)
    list_display = ("id", "DOI", "title")
    search_fields = ("title", "DOI")
    list_filter = (CountryFilter,)
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
    list_display = ("id", "type", "family", "onset", "offset", "band_lower_bound", "band_higher_bound","experiment_id")
    list_filter = (("family", admin.RelatedOnlyFieldListFilter),
                   ("type", admin.RelatedOnlyFieldListFilter),
                   "analysis_type")


class InterpretationAdmin(ImportExportModelAdmin):
    model = Interpretation
    list_filter = ("type", "theory")


class MeasureTypeAdmin(ImportExportModelAdmin):
    model = MeasureType


class MeasureAdmin(ImportExportModelAdmin):
    model = Measure
    list_filter = (("type", admin.RelatedOnlyFieldListFilter),)


class IsParentFilter(admin.SimpleListFilter):
    title = _("is parent paradigm")
    parameter_name = "is_parent"

    def lookups(self, request, model_admin):
        return [
            ("True", _("is a parent paradigm")),
            ("False", _("isn't a parent paradigm")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "True":
            return queryset.filter(parent__isnull=True)
        if self.value() == "False":
            return queryset.filter(parent__isnull=False)


class ParadigmAdmin(ImportExportModelAdmin):
    model = Paradigm
    list_filter = (IsParentFilter, ("parent", admin.RelatedOnlyFieldListFilter))


class SampleAdmin(ImportExportModelAdmin):
    model = Sample
    list_filter = ("type",)
    list_display = ("type", "total_size", "size_included", "experiment")


class ModalityTypeAdmin(ImportExportModelAdmin):
    model = ModalityType


class StimulusCategoryAdmin(ImportExportModelAdmin):
    model = StimulusCategory


class StimulusSubCategoryAdmin(ImportExportModelAdmin):
    model = StimulusSubCategory


class StimulusAdmin(ImportExportModelAdmin):
    model = Stimulus
    list_filter = (
    ("category", admin.RelatedOnlyFieldListFilter),
    ("sub_category", admin.RelatedOnlyFieldListFilter),
    ("modality", admin.RelatedOnlyFieldListFilter))


class TaskTypeAdmin(ImportExportModelAdmin):
    model = TaskType


class TaskAdmin(ImportExportModelAdmin):
    model = Task
    list_filter = (("type", admin.RelatedOnlyFieldListFilter),)


class TechniqueAdmin(ImportExportModelAdmin):
    model = Technique


class TheoryAdmin(ImportExportModelAdmin):
    model = Theory
    list_display = ("name", "parent_theory")

    @admin.display(empty_value="")
    def parent_theory(self, obj):
        if obj.parent is not None:
            return obj.parent.name
        else:
            return ""


# admin.site.disable_action('delete_selected')  # Site wide
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
