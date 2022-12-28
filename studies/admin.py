from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from studies.models import Study, Experiment


# Register your models here.

class ExperimentAdmin(ImportExportModelAdmin):
    model = Experiment
    list_filter = ()


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


admin.site.disable_action('delete_selected')  # Site wide
admin.site.register(Study, StudyAdmin)
admin.site.register(Experiment, ExperimentAdmin)
