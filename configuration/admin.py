from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from configuration.models import GraphImages


# Register your models here.

class GraphImagesAdmin(ImportExportModelAdmin):
    list_display = ("key", "image")


admin.site.register(GraphImages, GraphImagesAdmin)
