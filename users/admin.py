from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from users.models import Profile


# Register your models here.


class ProfileAdmin(ImportExportModelAdmin):
    fields = ("user",)


admin.site.register(Profile, ProfileAdmin)
