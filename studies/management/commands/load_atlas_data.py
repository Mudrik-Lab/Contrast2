from django.core.management.base import BaseCommand

from contrast_api.application_services.brain_images import get_AAL_Atlas_datasets


class Command(BaseCommand):
    help = "Load and cache the AAL atlas datasets for brain image generation"

    def handle(self, *args, **options):
        self.stdout.write("Loading AAL atlas datasets...")
        get_AAL_Atlas_datasets()
        self.stdout.write(self.style.SUCCESS("Successfully loaded and cached all atlas datasets"))
