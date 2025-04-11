import base64
import io
from typing import Dict

import pandas as pd
from nilearn import datasets, image, surface, plotting

from matplotlib.colors import LinearSegmentedColormap, to_rgba
import matplotlib.pyplot as plt

import nibabel as nib


class BrainViews:
    LATERAL = "lateral"
    MEDIAL = "medial"


import numpy as np

cross_version_mapping = {
    "Frontal_Inf_Orb_L": "Frontal_Inf_Orb_2_L",
    "Frontal_Mid_L": "Frontal_Mid_2_L",
    "Frontal_Sup_L": "Frontal_Sup_2_L",
    "Thal_RE_L": "Thal_Re_L",
    "Frontal_Sup_Med_L": "Frontal_Sup_Medial_L",
    "Thalamus_L": "Thal_AV_L",
    "Cingulate_Ant_L": "ACC_sub_L",
}
cross_version_mapping_one_to_many = {
    "Thalamus_L": [
        "Thal_AV_L",
        "Thal_LP_L",
        "Thal_VA_L",
        "Thal_VL_L",
        "Thal_VPL_L",
        "Thal_IL_L",
        "Thal_Re_L",
        "Thal_MDm_L",
        "Thal_MDl_L",
        "Thal_LGN_L",
        "Thal_MGN_L",
        "Thal_PuI_L",
        "Thal_PuM_L",
        "Thal_PuA_L",
        "Thal_PuL_L",
    ],  # {Thalamus includes all of these sub-regions}
    "Cingulate_Ant_L": ["ACC_sub_L", "ACC_pre_L", "ACC_sup_L"],  # {all of these areas are relevant}
}


def get_AAL_Atlas_datasets():
    fsaverage = datasets.fetch_surf_fsaverage(mesh="fsaverage6")
    aal = datasets.fetch_atlas_aal(version="3v2")
    return fsaverage, aal


class BrainImageCreatorService:
    def __init__(self, findings_df: pd.DataFrame, theory: str):
        self.findings_df = findings_df
        self.theory = theory
        self.theory_to_color_hex = {
            "Higher Order": "#6969B0",
            "Global Workspace": "#D76964",
            "Integrated Information": "#ECE76D",
            "First Order & Predictive Processing": "#60A7C2",
        }
        self.fsaverage, self.aal = get_AAL_Atlas_datasets()

    def create_brain_image(self) -> Dict:
        # process the dataframe
        if self.findings_df.empty:
            return {BrainViews.MEDIAL: "", BrainViews.LATERAL: "", "theory": self.theory}

        df = self.process_tags_interpretations(self.findings_df)

        # generate the normalized dataframe

        deduplicated_df = self.deduplicate_df(df)
        # create the brain image
        dfs = {}
        for theory in self.theory_to_color_hex.keys():
            normalized_df = self.generate_normalized_df(deduplicated_df, theory)
            dfs[theory] = normalized_df
        combined_df = pd.concat(dfs.values(), keys=dfs.keys(), names=["theory"])
        combined_df = combined_df.reset_index(level=0)
        combined_df.reset_index(drop=True, inplace=True)
        color = self.theory_to_color_hex[self.theory]
        brain_image_lateral = self.plot_brain_regions(
            theory=self.theory, color=color, dataframe=combined_df, view=BrainViews.LATERAL
        )
        brain_image_medial = self.plot_brain_regions(
            theory=self.theory, color=color, dataframe=combined_df, view=BrainViews.MEDIAL
        )

        return {BrainViews.MEDIAL: brain_image_medial, BrainViews.LATERAL: brain_image_lateral, "theory": self.theory}

    def create_cmap(self, frequencies, theory, color):
        color_list = [(0, (0, 0, 0, 0))]

        for frequency in sorted(list(set(frequencies))):
            color_list.append((frequency, to_rgba(color, alpha=frequency * 0.95)))
        color_list.append((1, to_rgba(color, alpha=1)))
        return LinearSegmentedColormap.from_list(name=theory, colors=color_list)

    def deduplicate_df(self, df: pd.DataFrame):
        # Group by 'AAL_Label' and aggregate the other columns
        grouped = df.groupby(["experiment_id", "aal_atlas_tags", "theory"])

        # Keep only the first row within each group
        deduplicated_df = grouped.first().reset_index()

        return deduplicated_df[["theory", "aal_atlas_tags", "experiment_id"]]

    def generate_normalized_df(self, df: pd.DataFrame, theory: str):
        # filter the big dataframe
        df_theory = df[df["theory"] == theory]

        # get the frequency of each label within the theory
        label_counts = df_theory["aal_atlas_tags"].value_counts()

        # normalize by the maximal frequency
        max_freq = label_counts.max()
        normalized_freq = label_counts / max_freq

        # create the final dataframe to feed the brain image generation
        normalized_df = pd.DataFrame(
            {
                "AAL_Label": normalized_freq.index,
                "area": normalized_freq.index,
                "experiments": pd.Series([df_theory["experiment_id"].nunique()] * len(normalized_freq)),
                "original_frequency": label_counts.values,
                "frequency": normalized_freq.values,  # normalized
            }
        )

        return normalized_df

    def process_tags_interpretations(self, df: pd.DataFrame):
        # Split the concatenated strings into lists
        df["aal_atlas_tags"] = df["AAL_atlas_tags"].str.split(" \\| ")
        df["interpretations"] = df["interpretations"].str.split(" \\| ")

        # Explode the DataFrame
        df = df.explode("aal_atlas_tags")
        df = df.explode("interpretations")

        # Split the interpretations into theory and type
        df[["theory", "theory_type"]] = df["interpretations"].str.split(" - ", expand=True)

        return df

    def plot_brain_regions(self, theory: str, color: str, dataframe: pd.DataFrame, view: str, format="png"):
        """
        Visualizes selected regions from the AAL atlas as a 2D surface mapping of a 3D brain surface.

        Parameters:
        - theory_color_mapping: dict, a mapping of theories to their color schemes.
        - dataframe: pd.DataFrame, a dataframe containing the AAL regions for each theory and their frequencies.

        Output:
        - Saves PNG files for each theory with the visualized regions.
        """
        # create an empty image to hold the combined regions
        aal_img = image.load_img(self.aal.maps)
        affine = aal_img.affine

        theory_df = dataframe[dataframe["theory"] == theory]
        frequencies = theory_df["frequency"]
        total = theory_df["experiments"].unique()[0]
        tags_count = theory_df["original_frequency"]
        max_num = max(tags_count)

        cmap = self.create_cmap(frequencies, theory, color)

        combined_img = self.combine_image_data(theory, dataframe, aal_img)
        new_combined_img = nib.Nifti1Image(combined_img, affine=affine)

        # Project volumetric data to surface
        texture = surface.vol_to_surf(new_combined_img, self.fsaverage.pial_left)

        # Create both views using the helper function
        return self.create_brain_plot(view, theory, total, max_num, texture, cmap, format)

    def get_areas_and_frequencies(self, theory, dataframe: pd.DataFrame):
        """
        this function takes in a dataframe and returns the areas and the frequencies
        as 2 seperate lists for a given theory (case sensitive).
        """
        theory_data = dataframe[dataframe["theory"] == theory]
        areas = theory_data["area"]
        frequencies = theory_data["frequency"]

        return areas, frequencies

    def get_aal_region_code_L(self, region: str):
        """
        this function takes in a region (string) and returns a dict including the region
        name (str) and the rightside and leftside atlas indices (int) for that region,
        if exists. if the region doesn't exist for that atlas, returns a tuple of
        region name and 0. case sensitive.
        """
        region = region.strip()
        if region.endswith("L"):
            name = region
        else:
            name = "_".join([region, "L"])

        try:
            region_code = self.aal.indices[self.aal.labels.index(name)]
        except ValueError:
            if name in cross_version_mapping.keys():
                try:
                    region_code = self.aal.indices[self.aal.labels.index(cross_version_mapping[name])]
                except ValueError:
                    return {"name": name, "region code": 0}
            else:
                return {"name": name, "region code": 0}

        return {"name": name, "region code": int(region_code)}

    def combine_image_data(self, theory_name: str, frequencies_dataframe: pd.DataFrame, img):
        regions, opacities = self.get_areas_and_frequencies(theory_name, frequencies_dataframe)
        left_hemisphere_regions = [self.get_aal_region_code_L(region)["region code"] for region in regions]

        combined_img_data = np.zeros(img.shape)

        # Loop through the defined regions and set them in the combined image
        for region, opacity in zip(left_hemisphere_regions, opacities):
            if region == 0:
                continue
            else:
                mask = (img.get_fdata() == region).astype(float)
                combined_img_data += mask * opacity

        return combined_img_data

    def create_brain_plot(self, view_type: str, theory, total, max_num, texture, cmap, format="png"):
        """Helper function to create and set up a brain visualization figure."""
        title = f"{theory}, N={total} \n {view_type.title()} View"

        fig = plt.figure(figsize=(10, 10))
        plt.subplots_adjust(bottom=0.15)

        plotting.plot_surf_stat_map(
            self.fsaverage.pial_left,
            texture,
            hemi="left",
            view=view_type,
            colorbar=True,
            cmap=cmap,
            darkness=1,
            bg_on_data=False,
            bg_map=self.fsaverage.sulc_left,
            threshold=None,
            avg_method="mean",
            title=title,
            figure=fig,
        )

        caption_text = f"Normalized color scale, where 1 is the most active region, N={max_num} experiments"
        fig.text(0.5, 0.05, caption_text, ha="center", va="bottom", fontsize=14)
        buffer = io.BytesIO()
        plt.savefig(buffer, format=format)
        plt.close(fig)
        buffer.seek(0)
        image_bytes = buffer.getvalue()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        return encoded_image
