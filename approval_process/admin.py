from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from approval_process.models import ApprovalProcess, ApprovalComment


# Register your models here.


class ApprovalCommentInline(admin.TabularInline):
    fields = ("text", "reviewer")
    model = ApprovalComment


class ApprovalProcessAdmin(ImportExportModelAdmin):
    model = ApprovalProcess
    search_fields = ("study__DOI", "study__title")
    list_display = ("study__title", "started_at", "status")
    list_filter = ("status",)  # TODO add filter for "stuck" in process approvals by date

    def study__title(self, obj):
        return obj.study.title

    def get_queryset(self, request):
        return super().get_queryset(request=request).select_related("study").prefetch_related("comments")

    inlines = [ApprovalCommentInline]
    # TODO: custom action for sending to reviewers


# TODO: find out how to show this admin to reviewers without the rest

admin.site.register(ApprovalProcess, ApprovalProcessAdmin)
