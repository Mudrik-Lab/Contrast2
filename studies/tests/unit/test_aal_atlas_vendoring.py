import gzip
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from contrast_api.application_services import brain_images
from contrast_api.application_services.brain_images import VENDORED_AAL_DIR, _ensure_aal_atlas


class EnsureAALAtlasTestCase(SimpleTestCase):
    """The atlas is vendored so the app never depends on gin.cnrs.fr being up.

    These run against the real files with no network stubbing on purpose: the
    whole point of vendoring is that there is no longer a boundary to mock.
    """

    def test_vendored_files_are_present_and_readable(self):
        nii_gz = VENDORED_AAL_DIR / "AAL3v1.nii.gz"
        xml = VENDORED_AAL_DIR / "AAL3v1.xml"

        self.assertTrue(nii_gz.exists(), f"missing vendored atlas volume at {nii_gz}")
        self.assertTrue(xml.exists(), f"missing vendored atlas labels at {xml}")

        with gzip.open(nii_gz, "rb") as f:
            header = f.read(4)
        # NIfTI-1 single file: first int32 is the 348-byte header length
        self.assertEqual(int.from_bytes(header, "little"), 348)

    def test_populates_cache_from_vendored_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "aal_3v2"
            with mock.patch.object(brain_images, "AAL_DATA_DIR", cache):
                _ensure_aal_atlas()

            nii = cache / "AAL3" / "AAL3v1.nii"
            xml = cache / "AAL3" / "AAL3v1.xml"
            self.assertTrue(nii.exists())
            self.assertTrue(xml.exists())
            # nilearn reads the uncompressed volume, so it must be fully expanded
            with gzip.open(VENDORED_AAL_DIR / "AAL3v1.nii.gz", "rb") as f:
                self.assertEqual(nii.read_bytes(), f.read())
            # no partial files left behind
            self.assertEqual(list((cache / "AAL3").glob("*.part")), [])

    def test_is_idempotent_and_leaves_existing_cache_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "aal_3v2"
            with mock.patch.object(brain_images, "AAL_DATA_DIR", cache):
                _ensure_aal_atlas()
                nii = cache / "AAL3" / "AAL3v1.nii"
                first_mtime = nii.stat().st_mtime_ns

                _ensure_aal_atlas()
                self.assertEqual(nii.stat().st_mtime_ns, first_mtime)
