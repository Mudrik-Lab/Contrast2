# AAL3v2 atlas (vendored)

The two files nilearn needs to satisfy `fetch_atlas_aal(version="3v2")`:

| File | Purpose |
|---|---|
| `AAL3v1.nii.gz` | Parcellation volume. Decompressed to `AAL3v1.nii` at runtime — nilearn looks for the uncompressed name. |
| `AAL3v1.xml` | Region index/label table. |

`fetch_atlas_aal` requests exactly `AAL3/AAL3v1.nii` and `AAL3/AAL3v1.xml` and skips
its download when both are already present, so nothing else from the upstream
archive is needed.

These are vendored rather than downloaded because the upstream host
(`gin.cnrs.fr`) has repeatedly been unavailable, and on Heroku a release-phase
download cannot persist to the web dynos anyway — the dyno filesystem is
ephemeral. At ~49 KB the atlas is cheaper to keep in the repo than to fetch.

## License

AAL3 is distributed by the Neurofunctional Imaging Group (GIN, UMR5296,
Bordeaux, France) as copyright freeware **under the terms of the GNU General
Public License** — see the AAL3 User Guide (AAL3v2, 5 April 2024), which states
the GPL was added to the upstream readme in that release. This repository is
GPL-3.0, so redistribution here is license-compatible.

Upstream: https://www.gin.cnrs.fr/en/tools/aal/

## Citation

Work using this atlas must cite:

- Tzourio-Mazoyer N, Landeau B, Papathanassiou D, Crivello F, Etard O, Delcroix N,
  Mazoyer B, Joliot M. *Automated anatomical labelling of activations in SPM using a
  macroscopic anatomical parcellation of the MNI MRI single subject brain.*
  NeuroImage 2002; 15: 273-289.
- Rolls ET, Huang C, Lin C, Feng J, Joliot M. *Automated anatomical labelling atlas 3.*
  NeuroImage 2020; 206: 116189.
