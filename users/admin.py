from django.contrib import admin
from django.contrib.admin import FieldListFilter
from import_export.admin import ImportExportModelAdmin

from users.models import Profile


# Register your models here.


class ProfileAdmin(ImportExportModelAdmin):
    list_display = ("user", "email", "country_of_residence", "has_ASSC_membership", "academic_stage")
    list_filter = ("has_ASSC_membership", "academic_stage")

    @admin.display
    def email(self, obj):
        return obj.user.email


admin.site.register(Profile, ProfileAdmin)
