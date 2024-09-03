from typing import List

from django.contrib import admin, messages
from django.db.models import Prefetch
from django.forms import forms
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin, ImportExportMixin, ExportActionMixin
from django.utils.translation import gettext_lazy as _
from django_countries import countries

from contrast_api.admin_utils import SimpleHistoryWithDeletedAdmin
from contrast_api.domain_services.study_lifecycle import StudyLifeCycleService
from contrast_api.choices import InterpretationsChoices
from studies.models import (
    Study,
    Experiment,
    Author,
    ConsciousnessMeasure,
    ConsciousnessMeasureType,
    ConsciousnessMeasurePhaseType,
    FindingTagFamily,
    FindingTagType,
    FindingTag,
    Interpretation,
    MeasureType,
    Measure,
    Paradigm,
    Sample,
    ModalityType,
    TaskType,
    Task,
    Technique,
    Theory,
    AggregatedInterpretation,
)
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, Stimulus
from rangefilter.filters import NumericRangeFilter

from studies.resources.full_experiment import FullExperimentResource
from uncontrast_studies.models import UnConExperiment
from uncontrast_studies.resources.full_experiment import FullUnConExperimentResource


class BaseContrastAdmin(ImportExportMixin, SimpleHistoryWithDeletedAdmin):
    pass


# Register your models here.
class ExperimentRelatedInline:
    show_change_link = True
    extra = 0
    fk_name = "experiment"

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


class TheoryInterpretationFilter(admin.SimpleListFilter):
    title = "Theory Interpretations"
    parameter_name = "theory_interpretation"

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


class ExperimentAdmin(BaseContrastAdmin):
    list_display = (
        "id",
        "type_of_consciousness",
        "is_reporting",
        "theory_driven",
    )
    model = Experiment
    fields = (
        "type_of_consciousness",
        "is_reporting",
        "theory_driven",
        "theory_driven_theories",
        "results_summary",
        "paradigms_notes",
        "tasks_notes",
        "consciousness_measures_notes",
        "stimuli_notes",
        "sample_notes",
        "techniques",
        "paradigms",
    )
    search_fields = (
        "study__DOI",
        "study__title",
        "results_summary",
        "paradigms_notes",
        "tasks_notes",
        "consciousness_measures_notes",
        "stimuli_notes",
    )
    list_filter = ("type_of_consciousness", "type", "is_reporting", "theory_driven", "study__approval_status")
    filter_horizontal = ("paradigms", "techniques")
    resource_class = FullExperimentResource
    inlines = (
        InterpretationInline,
        SampleInline,
        FindingTagInline,
        MeasureInline,
        ConsciousnessMeasureInline,
        StimulusInline,
    )

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
    fields = (
        "type_of_consciousness",
        "is_reporting",
        "theory_driven",
        "theory_driven_theories",
        "results_summary",
        "paradigms_notes",
        "tasks_notes",
        "consciousness_measures_notes",
        "stimuli_notes",
        "sample_notes",
        "techniques",
        "paradigms",
    )
    # fields =
    show_change_link = True
    extra = 0

    # inlines = ( # need to migrate this to be sub inline
    #     InterpretationInline,
    #     SampleInline,
    #     FindingTagInline,
    #     MeasureInline,
    #     ConsciousnessMeasureInline,
    #     StimulusInline,
    # )

    def get_queryset(self, request):
        qs = super().get_queryset(request=request)
        # trying to optimize this view, but alas, currently the custom Prefetch doesn't seem to be working
        return (
            qs.select_related("study")
            .prefetch_related(
                Prefetch(
                    "paradigms",
                    queryset=Paradigm.objects.filter(parent__isnull=False).select_related("parent", "parent__parent"),
                )
            )
            .prefetch_related("techniques")
        )

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


class CountryFilter(admin.SimpleListFilter):
    title = "Country"
    parameter_name = "country"

    def lookups(self, request, model_admin):
        # Get a list of all distinct countries that exist in the database
        existing_countries = model_admin.get_queryset(request).values_list("countries", flat=True).distinct()
        flattened_existing_countries = sorted(
            set(country for the_countries in existing_countries for country in the_countries)
        )

        # Create a list of tuples for the filter dropdown
        # Each tuple contains the country code and name
        return [(country, countries.name(country)) for country in flattened_existing_countries]

    def queryset(self, request, queryset):
        # If a country code is selected in the filter,
        # return only the studies that have that country
        if self.value():
            return queryset.filter(countries__contains=[self.value()])


class JournalFilter(admin.SimpleListFilter):
    title = "Journal"
    parameter_name = "journal"

    def lookups(self, request, model_admin):
        # Get a list of all distinct countries that exist in the database
        existing_journals = (
            model_admin.get_queryset(request).values_list("abbreviated_source_title", flat=True).distinct()
        )

        # Create a list of tuples for the filter dropdown
        # Each tuple contains the country code and name
        return [(journal, journal.capitalize()) for journal in existing_journals if journal is not None] + [
            ("None", "None")
        ]

    def queryset(self, request, queryset):
        # If a country code is selected in the filter,
        # return only the studies that have that country
        if self.value() == "None":
            return queryset.filter(abbreviated_source_title__isnull=True)
        elif self.value():
            return queryset.filter(abbreviated_source_title__in=[self.value()])


@admin.action(description="rejecting a pending study")
def reject_study(modeladmin, request, queryset):
    service = StudyLifeCycleService()
    service.rejected(request.user, queryset)
    messages.info(request, "Rejected studies")


@admin.action(description="Returning studies to pending status")
def pending_study(modeladmin, request, queryset):
    service = StudyLifeCycleService()
    service.pending(request.user, queryset)
    messages.info(request, "pending studies")


@admin.action(description="approving a pending study")
def approve_study(modeladmin, request, queryset):
    service = StudyLifeCycleService()
    service.approved(request.user, queryset)
    messages.info(request, "Approved studies")


@admin.action(description="moving a study to review")
def review_study(modeladmin, request, queryset):
    service = StudyLifeCycleService()
    service.reviewed(request.user, queryset)
    messages.info(request, "Reviewing studies")


class StudyAdmin(BaseContrastAdmin, ExportActionMixin):
    from uncontrast_studies.admin import UnConExperimentInline
    model = Study
    resource_classes = [
        FullExperimentResource,
        FullUnConExperimentResource,
    ]  # Note: we're return experiments, not studies
    filter_horizontal = ("authors",)
    list_display = ("id", "DOI", "title", "abbreviated_source_title", "is_author_submitter", "submitter_name")
    search_fields = ("title", "DOI", "submitter__email")
    list_filter = (
        "type",
        "approval_status",
        "is_author_submitter",
        CountryFilter,
        JournalFilter,
        ("year", NumericRangeFilter),
    )
    actions = (approve_study, reject_study, review_study, pending_study)
    inlines = [ExperimentInline, UnConExperimentInline]
    """
    Note: a lot of methods here are inherited from the base export action because 
    we both customize it to export not studies but experiments, and now we need to adapt it
    to uncontrast experiments also
    """

    def export_uncontrast_admin_action(self, request, queryset):
        """
        Exports the selected rows using file_format.
        """
        export_format = request.POST.get("file_format")

        if not export_format:
            messages.warning(request, _("You must select an export format."))
        else:
            formats = self.get_export_formats()
            file_format = formats[int(export_format)]()

            export_data = self.get_uncontrast_export_data(
                file_format, queryset, request=request, encoding=self.to_encoding
            )
            content_type = file_format.get_content_type()
            response = HttpResponse(export_data, content_type=content_type)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (
                self.get_export_filename(request, queryset, file_format),
            )
            return response

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.update(
            export_uncontrast_admin_action=(
                type(self).export_uncontrast_admin_action,
                "export_uncontrast_admin_action",
                _("Export selected uncontrast %(verbose_name_plural)s"),
            )
        )
        return actions

    @property
    def media(self):
        super_media = super().media
        return forms.Media(
            js=super_media._js + ["studies/action_formats.js"],
            css=super_media._css,
        )

    def get_data_for_export(self, request, queryset, *args, **kwargs):
        export_form = kwargs.get("export_form")
        if request.POST.get("action") == "export_uncontrast_admin_action":
            export_class = self.resource_classes[1]
        else:
            export_class = self.choose_export_resource_class(export_form, request)
        export_resource_kwargs = self.get_export_resource_kwargs(request, *args, **kwargs)
        cls = export_class(**export_resource_kwargs)
        export_data = cls.export(queryset=queryset, **kwargs)
        return export_data

    def get_uncontrast_export_data(self, file_format, request, queryset, **kwargs):
        uncontrast_experiments_qs = UnConExperiment.objects.related().filter(study__in=queryset)
        return super().get_export_data(file_format, request, queryset=uncontrast_experiments_qs, **kwargs)

    def get_export_data(self, file_format, request, queryset, **kwargs):
        experiments_qs = Experiment.objects.related().filter(study__in=queryset)
        return super().get_export_data(file_format, request, queryset=experiments_qs, **kwargs)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("submitter").prefetch_related("authors")

    def submitter_name(self, obj):
        return obj.submitter and obj.submitter.username


class AuthorAdmin(BaseContrastAdmin):
    model = Author
    list_display = ("id", "name")
    search_fields = (
        "id",
        "name",
    )


class ConsciousnessMeasureAdmin(BaseContrastAdmin):
    list_display = ("phase", "type", "experiment_id")
    model = ConsciousnessMeasure
    list_filter = ("phase", "type", TheoryInterpretationFilter)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


class ConsciousnessMeasureTypeAdmin(ImportExportModelAdmin):
    model = ConsciousnessMeasureType
    list_display = ("id", "name")


class ConsciousnessMeasurePhaseTypeAdmin(ImportExportModelAdmin):
    model = ConsciousnessMeasurePhaseType
    list_display = ("id", "name")


class FindingTagFamilyAdmin(ImportExportModelAdmin):
    model = FindingTagFamily
    list_display = ("id", "name")


class FindingTagTypeAdmin(ImportExportModelAdmin):
    model = FindingTagType
    list_display = ("id", "name", "family")
    list_filter = ("family",)
    search_fields = ("name",)


class FindingTagAdmin(BaseContrastAdmin):
    model = FindingTag
    search_fields = ("notes",)
    list_display = (
        "id",
        "type",
        "family",
        "onset",
        "offset",
        "band_lower_bound",
        "band_higher_bound",
        "direction",
        "AAL_atlas_tag",
        "notes",
        "experiment_id",
    )
    list_filter = (
        ("family", admin.RelatedOnlyFieldListFilter),
        ("type", admin.RelatedOnlyFieldListFilter),
        ("onset", NumericRangeFilter),
        ("offset", NumericRangeFilter),
        ("band_lower_bound", NumericRangeFilter),
        ("band_higher_bound", NumericRangeFilter),
        ("technique", admin.RelatedOnlyFieldListFilter),
        "direction",
        "analysis_type",
        "is_NCC",
        TheoryInterpretationFilter,
    )


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


class MeasureAdmin(BaseContrastAdmin):
    model = Measure
    search_fields = ("notes",)
    list_display = ("id", "type", "notes", "experiment_id")
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


class ParadigmAdmin(BaseContrastAdmin):
    model = Paradigm
    list_display = ("name", "sub_type")
    list_filter = (IsParentFilter, ("parent", admin.RelatedOnlyFieldListFilter))
    search_fields = ("name", "sub_type")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent", "parent__parent")


class SampleAdmin(BaseContrastAdmin):
    model = Sample
    list_filter = (
        "type",
        TheoryInterpretationFilter,
        ("total_size", NumericRangeFilter),
        ("size_included", NumericRangeFilter),
    )
    list_display = ("type", "total_size", "size_included", "experiment")


class ModalityTypeAdmin(ImportExportModelAdmin):
    model = ModalityType
    list_display = ("id", "name")


class StimulusCategoryAdmin(ImportExportModelAdmin):
    model = StimulusCategory
    list_display = ("id", "name")
    search_fields = ("name",)


class StimulusSubCategoryAdmin(ImportExportModelAdmin):
    list_display = ("id", "name", "parent")
    model = StimulusSubCategory
    list_filter = ("parent",)
    search_fields = ("name",)


class StimulusAdmin(BaseContrastAdmin):
    list_display = ("id", "category", "sub_category", "modality", "duration", "experiment_id")
    model = Stimulus
    list_filter = (
        ("category", admin.RelatedOnlyFieldListFilter),
        ("sub_category", admin.RelatedOnlyFieldListFilter),
        ("modality", admin.RelatedOnlyFieldListFilter),
        TheoryInterpretationFilter,
    )

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("category", "sub_category", "modality", "sub_category__parent")
        )


class TaskTypeAdmin(ImportExportModelAdmin):
    model = TaskType
    list_display = ("id", "name")
    search_fields = ("name",)


class TaskAdmin(BaseContrastAdmin):
    list_display = ("id", "type", "experiment_id")
    model = Task
    list_filter = (("type", admin.RelatedOnlyFieldListFilter), TheoryInterpretationFilter)


class TechniqueAdmin(BaseContrastAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    model = Technique


class TheoryAdmin(BaseContrastAdmin):
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
