from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from approval_process.models import ApprovalProcess, ApprovalComment


# Register your models here.

class ApprovalCommentInline(admin.TabularInline):
    fields = ("text", "reviewer", "created_at")
    model = ApprovalComment


class ApprovalProcessAdmin(ImportExportModelAdmin):
    fields = ("started_at", "status", "study")
    list_filter = ("status",)

    inlines = [
        ApprovalCommentInline
    ]
    #TODO: custom action for sending to reviewers


admin.site.register(ApprovalProcess, ApprovalProcessAdmin)
