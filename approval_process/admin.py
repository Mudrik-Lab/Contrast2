from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from approval_process.models import ApprovalProcess, ApprovalComment


# Register your models here.

class ApprovalCommentInline(admin.TabularInline):
    fields = ("text", "reviewer", "created_at")
    model = ApprovalComment


class ApprovalProcessAdmin(ImportExportModelAdmin):
    model = ApprovalProcess
    fields = ("started_at", "status", "study")
    list_filter = ("status",)  # TODO add filter for "stuck" in process approvals by date

    # TODO add drop down filters for reviewers
    def get_queryset(self, request):
        return super().get_queryset(request=request).prefetch_related("comments")

    inlines = [
        ApprovalCommentInline
    ]
    # TODO: custom action for sending to reviewers


# TODO: find out how to show this admin to reviewers without the rest

admin.site.register(ApprovalProcess, ApprovalProcessAdmin)
