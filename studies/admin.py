from typing import List

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _
from django_countries import countries

from studies.choices import InterpretationsChoices
from studies.models import Study, Experiment, Author, ConsciousnessMeasure, ConsciousnessMeasureType, \
    ConsciousnessMeasurePhaseType, FindingTagFamily, FindingTagType, FindingTag, Interpretation, MeasureType, Measure, \
    Paradigm, Sample, ModalityType, TaskType, Task, Technique, Theory, AggregatedInterpretation
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, Stimulus
from rangefilter.filters import NumericRangeFilterBuilder, NumericRangeFilter

from studies.resources.full_experiment import FullExperimentResource


# Register your models here.
class ExperimentRelatedInline:
    show_change_link = True
    extra = 0
    fk_name = "experiment"

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


class TheoryInterpretationFilter(admin.SimpleListFilter):
    title = 'Theory Interpretations'
    parameter_name = 'theory_interpretation'

    def lookups(self, request, model_admin):
        lookups = []
        theories: List[str] = Theory.objects.filter(parent__isnull=True).values_list("name", flat=True)
        for interpretation_value, interpretation_label in InterpretationsChoices.choices:
            for theory_name in theories:
                value = f"{theory_name}_{interpretation_value}"
                label = f"{theory_name.capitalize()} {interpretation_value.capitalize()}"
                lookups.append((value, label))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            theory_name, relation_type = self.value().split("_")
            interpretations = Interpretation.objects.filter(type=relation_type, theory__parent__name=theory_name)
            return queryset.filter(experiment__in=interpretations.values("experiment"))


class SampleInline(ExperimentRelatedInline, admin.StackedInline):
    model = Sample


class StimulusInline(ExperimentRelatedInline, admin.StackedInline):
    model = Stimulus


class FindingTagInline(ExperimentRelatedInline, admin.TabularInline):
    model = FindingTag


class MeasureInline(ExperimentRelatedInline, admin.StackedInline):
    model = Measure


class InterpretationInline(ExperimentRelatedInline, admin.TabularInline):
    model = Interpretation


class ConsciousnessMeasureInline(ExperimentRelatedInline, admin.StackedInline):
    model = ConsciousnessMeasure


class ExperimentAdmin(ImportExportModelAdmin):

    # todo add theory to display
    list_display = ("id", "type_of_consciousness", "is_reporting", "theory_driven", "study__title",)
    model = Experiment
    fields = ("type_of_consciousness", "is_reporting", "theory_driven", "techniques", "paradigms")
    list_filter = ("type_of_consciousness", "type", "is_reporting", "theory_driven", "study__approval_status")
    filter_horizontal = ("paradigms", "techniques")
    resource_class = FullExperimentResource
    inlines = (
        InterpretationInline,
        SampleInline,
        FindingTagInline,
        MeasureInline,
        ConsciousnessMeasureInline,
        StimulusInline)

    def get_queryset(self, request):
        qs = self.model._default_manager.related()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
        # trying to optimize this view, but alas, currently the custom Prefetch doesn't seem to be working
        

    @admin.display(empty_value="")
    def study__title(self, obj):
        return obj.study.title


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
    list_display = ("phase", "type", "description", "experiment_id")
    search_fields = ('description',)
    model = ConsciousnessMeasure
    list_filter = ("phase", "type", TheoryInterpretationFilter)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


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
    search_fields = ('notes',)
    list_display = ("id", "type", "family", "onset", "offset", "band_lower_bound", "band_higher_bound",
                    'correlation_sign', 'AAL_atlas_tag', 'notes', "experiment_id")
    list_filter = (("family", admin.RelatedOnlyFieldListFilter),
                   ("type", admin.RelatedOnlyFieldListFilter),
                   ("onset", NumericRangeFilter),
                   ("offset", NumericRangeFilter),
                   ("band_lower_bound", NumericRangeFilter),
                   ("band_higher_bound", NumericRangeFilter),
                   ("technique", admin.RelatedOnlyFieldListFilter),
                   'correlation_sign',
                   "analysis_type",
                   TheoryInterpretationFilter)


class InterpretationAdmin(ImportExportModelAdmin):
    list_display = ("id", "type", "experiment_id", "theory")
    model = Interpretation
    list_filter = ("type", "theory")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("theory", "theory__parent")


class AggregatedInterpretationAdmin(ImportExportModelAdmin):
    list_display = ("id", "type", "parent_theory_names")
    model = AggregatedInterpretation
    list_filter = ("type", "parent_theory_names")


class MeasureTypeAdmin(ImportExportModelAdmin):
    model = MeasureType


class MeasureAdmin(ImportExportModelAdmin):
    model = Measure
    search_fields = ('notes',)
    list_display = ('id', 'type', 'notes', 'experiment_id')
    list_filter = (("type", admin.RelatedOnlyFieldListFilter), TheoryInterpretationFilter)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent", "parent__parent")


class SampleAdmin(ImportExportModelAdmin):
    model = Sample
    list_filter = ("type", TheoryInterpretationFilter)
    list_display = ("type", "total_size", "size_included", "experiment")


class ModalityTypeAdmin(ImportExportModelAdmin):
    model = ModalityType


class StimulusCategoryAdmin(ImportExportModelAdmin):
    model = StimulusCategory


class StimulusSubCategoryAdmin(ImportExportModelAdmin):
    list_display = ("id", "name", "parent")
    model = StimulusSubCategory


class StimulusAdmin(ImportExportModelAdmin):
    list_display = ("id", "category", "sub_category", "modality", "duration", "description", "experiment_id")
    model = Stimulus
    search_fields = ('description',)
    list_filter = (
        ("category", admin.RelatedOnlyFieldListFilter),
        ("sub_category", admin.RelatedOnlyFieldListFilter),
        ("modality", admin.RelatedOnlyFieldListFilter),
        TheoryInterpretationFilter)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category", "sub_category", "modality",
                                                            "sub_category__parent")


class TaskTypeAdmin(ImportExportModelAdmin):
    model = TaskType


class TaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'type', 'description', 'experiment_id')
    search_fields = ('description',)
    model = Task
    list_filter = (("type", admin.RelatedOnlyFieldListFilter), TheoryInterpretationFilter)


class TechniqueAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')
    model = Technique


class TheoryAdmin(ImportExportModelAdmin):
    model = Theory
    list_display = ("name", "parent_theory")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent", "parent__parent")

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
admin.site.register(AggregatedInterpretation, AggregatedInterpretationAdmin)
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
