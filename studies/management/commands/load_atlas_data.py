import os
import ssl
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from django.core.management.base import BaseCommand
from nilearn import datasets

AAL_URL = "https://www.gin.cnrs.fr/wp-content/uploads/AAL3v2_for_SPM12.tar.gz"
AAL_DATA_DIR = Path.home() / "nilearn_data" / "aal_3v2"


class Command(BaseCommand):
    help = "Load and cache the AAL atlas datasets for brain image generation"

    def _ensure_aal_atlas(self):
        """Download and extract AAL atlas manually if not already cached.

        nilearn's fetch_atlas_aal uses an SSL connection that fails on
        some environments (e.g. Heroku). Pre-downloading the archive
        avoids the issue.
        """
        if AAL_DATA_DIR.exists() and any(AAL_DATA_DIR.iterdir()):
            self.stdout.write(f"AAL atlas already cached at {AAL_DATA_DIR}")
            return

        self.stdout.write(f"AAL atlas not found at {AAL_DATA_DIR}, downloading manually...")
        AAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
        # we need this as the site is broken
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with urllib.request.urlopen(AAL_URL, context=ctx) as response:
                with open(tmp_path, "wb") as out_file:
                    out_file.write(response.read())
            self.stdout.write("Download complete, extracting...")
            with tarfile.open(tmp_path, "r:gz") as tar:
                tar.extractall(path=AAL_DATA_DIR)
            self.stdout.write(f"Extracted AAL atlas to {AAL_DATA_DIR}")
        finally:
            os.unlink(tmp_path)

    def handle(self, *args, **options):
        self.stdout.write("Loading AAL atlas datasets...")

        # Load and cache fsaverage dataset
        self.stdout.write("Loading fsaverage dataset...")
        fsaverage = datasets.fetch_surf_fsaverage(mesh="fsaverage5")
        self.stdout.write(f"Loaded fsaverage dataset: {fsaverage.keys()}")

        # Pre-download AAL atlas to avoid SSL issues with nilearn's fetcher
        self._ensure_aal_atlas()

        # Load and cache AAL atlas
        self.stdout.write("Loading AAL atlas...")
        aal = datasets.fetch_atlas_aal(version="3v2")
        self.stdout.write(f"Loaded AAL atlas: {aal.keys()}")

        self.stdout.write(self.style.SUCCESS("Successfully loaded and cached all atlas datasets"))
