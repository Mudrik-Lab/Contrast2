from django.core.management.base import BaseCommand
from nilearn import datasets


class Command(BaseCommand):
    help = "Load and cache the AAL atlas datasets for brain image generation"

    def handle(self, *args, **options):
        self.stdout.write("Loading AAL atlas datasets...")

        # Load and cache fsaverage dataset
        self.stdout.write("Loading fsaverage dataset...")
        fsaverage = datasets.fetch_surf_fsaverage(mesh="fsaverage5")
        self.stdout.write(f"Loaded fsaverage dataset: {fsaverage.keys()}")

        # Load and cache AAL atlas
        self.stdout.write("Loading AAL atlas...")
        aal = datasets.fetch_atlas_aal(version="3v2")
        self.stdout.write(f"Loaded AAL atlas: {aal.keys()}")

        self.stdout.write(self.style.SUCCESS("Successfully loaded and cached all atlas datasets"))
