import base64
import functools
import gc
import io
import logging
from typing import Dict

import pandas as pd
import numpy as np
from nilearn import datasets, image, surface, plotting
from matplotlib.colors import LinearSegmentedColormap, to_rgba
import matplotlib.pyplot as plt
import nibabel as nib
from configuration.initial_setup import ParentTheories

logger = logging.getLogger(__name__)


class BrainViews:
    LATERAL = "lateral"
    MEDIAL = "medial"


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
    "Cingulate_Ant_L": ["ACC_sub_L", "ACC_pre_L", "ACC_sup_L"],
}


# @functools.cache
def get_AAL_Atlas_datasets():
    fsaverage = datasets.fetch_surf_fsaverage(mesh="fsaverage5")
    aal = datasets.fetch_atlas_aal(version="3v2")
    return fsaverage.pial_left, fsaverage.sulc_left, aal


class BrainImageCreatorService:
    def __init__(self, findings_df: pd.DataFrame, theory: str):
        self.findings_df = findings_df
        self.theory = theory
        self.theory_to_color_hex = {
            ParentTheories.HIGHER_ORDER: "#6969B0",
            ParentTheories.GLOBAL_WORKSPACE: "#D76964",
            ParentTheories.INTEGRATED_INFORMATION: "#ECE76D",
            ParentTheories.FIRST_ORDER_AND_PREDICTIVE_PROCESSING: "#60A7C2",
        }
        self.fsaverage_pial_left, self.fsaverage_sulc_left, self.aal = get_AAL_Atlas_datasets()

    def create_brain_image(self) -> Dict:
        # process the dataframe
        if self.findings_df.empty:
            return {
                BrainViews.MEDIAL: "",
                BrainViews.LATERAL: "",
                "theory": self.theory,
                "title text": "",
                "caption text": "",
            }

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
        brain_image_medial, title, caption_text = self.plot_brain_regions(
            theory=self.theory, color=color, dataframe=combined_df, view=BrainViews.MEDIAL
        )
        brain_image_lateral, title, caption_text = self.plot_brain_regions(
            theory=self.theory, color=color, dataframe=combined_df, view=BrainViews.LATERAL
        )
        gc.collect()

        return {
            BrainViews.MEDIAL: brain_image_medial,
            BrainViews.LATERAL: brain_image_lateral,
            "theory": self.theory,
            "title_text": title,
            "caption_text": caption_text,
            "color": color,
        }

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

    def plot_brain_regions(self, theory: str, color: str, dataframe: pd.DataFrame, view: str, save_format="png"):
        """
        Visualizes selected regions from the AAL atlas as a 2D surface mapping of a 3D brain surface.

        Parameters:
        - theory: str the name of the theory
        - color: str hex value of the base color of theory
        - dataframe: pd.DataFrame, a dataframe containing the AAL regions for each theory and their frequencies.
        - view: str lateral or medial
        - save_format: Enum[str] ['png','svg']

        Output:
        - Saves PNG files for each theory with the visualized regions.
        """
        logger.info(f"Starting to process brain image for {theory} and view {view} ")
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
        texture = surface.vol_to_surf(new_combined_img, self.fsaverage_pial_left)
        logger.info(f"Plotting {theory} for {view} view")
        result = self.create_brain_plot(view, texture, cmap, save_format)
        title = f"{theory}, N={total}"
        caption_text = f"Normalized color scale, where 1 is the most active region, N={max_num} experiments"

        logger.info(f"Finished Plotting {theory} for {view} view")
        return result, title, caption_text

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
        name (str) and the  leftside atlas indices (int) for that region,
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

    def create_brain_plot(self, view_type: str, texture, cmap, file_format="png"):
        """Helper function to create and set up a brain visualization figure."""
        title = f"{view_type.title()} View"
        fig = plt.figure(figsize=(10, 10), dpi=90)

        plotting.plot_surf_stat_map(
            self.fsaverage_pial_left,
            texture,
            hemi="left",
            view=view_type,
            colorbar=False,
            cmap=cmap,
            darkness=1,
            bg_on_data=False,
            bg_map=self.fsaverage_sulc_left,
            threshold=None,
            title=title,
            figure=fig,
        )

        buffer = io.BytesIO()
        plt.savefig(buffer, format=file_format, dpi=90)
        plt.close(fig)
        buffer.seek(0)
        image_bytes = buffer.getvalue()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        return encoded_image
