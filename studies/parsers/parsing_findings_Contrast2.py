import re

from studies.choices import AnalysisTypeChoices, DirectionChoices

# constants
ITEM_SEP = "+"
FINDING_INNER_S_SEP = "<"
FINDING_INNER_E_SEP = ">"
NEGATIVE_TAG = "-"
INNER_ITEM_SEP = "&"
START_FINDING_SEP = "("
END_FINDING_SEP = ")"
COMMENT_CHAR = "#"
UNINITIALIZED_VAL = None
TEMPORAL_MS = "ms"
TEMPORAL_NEGATIVE_TIMING_SIGN = "!"
TEMPORAL_APPROX_SIGN = "~"
ONSET_OFFSET_SEP = "-"
FREQUENCY_DATA_SEP = " "
FREQ_DIRECTION_DEF_VAL = "Positive"
FREQ_DIRECTION_NEGATIVE = "Neg"
FREQ_BAND_DEF_IDX = 1
FREQUENCY_HZ = "Hz"


class FindingTagDataError(Exception):
    pass


# a helper function that extracts and fills a 'finding class' with onset and offset information
def fill_temporal_util(finding, txt):
    # remove ms
    clean_temporal_txt = txt.replace(TEMPORAL_MS, "")
    # replace ! with - (we use - as a  separator for timing / bands )
    temporal_split = [
        time.replace(TEMPORAL_NEGATIVE_TIMING_SIGN, "-") for time in clean_temporal_txt.split(ONSET_OFFSET_SEP)
    ]
    temporal_split = [t.replace(TEMPORAL_APPROX_SIGN, "") for t in temporal_split]
    finding.onset = temporal_split[0].replace(FINDING_INNER_E_SEP, "").strip()
    # remove trailing >
    if len(temporal_split) > 1:
        finding.offset = temporal_split[1].replace(FINDING_INNER_E_SEP, "").strip()
    else:
        finding.offset = finding.onset
    if finding.onset == "":
        finding.onset = UNINITIALIZED_VAL
        finding.offset = UNINITIALIZED_VAL


# we define a base finding class which performs basic processing, and includes basic data types
# that should be shared across finding tags
#           Optional
# TAG (#COMMENT / COMMENT)


class BaseFinding:
    def __init__(self, tag_code, txt):
        # save all findings, but show in graphs only relevant findings, encoded in 'is_NCC'
        self.finding_txt = txt
        if tag_code:
            self.tag = tag_code.replace(NEGATIVE_TAG, "")
            self.is_NCC = tag_code[0] != NEGATIVE_TAG
        else:
            raise FindingTagDataError()
        self.comment = UNINITIALIZED_VAL
        self.technique = UNINITIALIZED_VAL
        # decode finding_txt right after initialization
        self.decode()

    def decode(self):
        # comments are written after # or as free text in basic tags (not temporal/spatial/frequency tags)
        if COMMENT_CHAR in self.finding_txt:
            # we expect a single comment char
            comment_split = self.finding_txt.split(COMMENT_CHAR)
            self.comment = comment_split[1].strip()
            self.finding_txt = comment_split[0]
        else:
            # if there is no comment char, the information inside the parenthesis is a "comment"
            self.comment = self.finding_txt
        if FINDING_INNER_S_SEP in self.finding_txt:
            # technique information is only relevant for temporal/spatial/frequency tags but it may appearing all three.
            technique_split = self.finding_txt.rsplit(FINDING_INNER_S_SEP, 1)
            # if it was encoded, technique will always appear last, but the last < may also encode temporal finding
            if TEMPORAL_MS not in technique_split[-1]:
                self.finding_txt = technique_split[0].strip()
                self.technique = technique_split[-1].strip().replace(FINDING_INNER_E_SEP, "")
        # if the technique is not explict,, fill from the 'techniques' parameter (here stays uninitialized)


# inherits from base tag, includes spatial specific information
#      Optional Optional
# TAG (AREA     #COMMENT)
class SpatialFinding(BaseFinding):
    def __init__(self, tag, txt):
        self.area = UNINITIALIZED_VAL
        super().__init__(tag, txt)

    def decode(self):
        super().decode()
        # area is optional
        if self.tag in finding_tag_to_area:
            self.area = finding_tag_to_area[self.tag]
        else:
            self.area = self.finding_txt.strip()


# inherits from base tag, includes temporal specific information
#                         Optional    Optional
# TAG (ONSET-OFFSETms   <TECHNIQUE>   #COMMENT)
class TemporalFinding(BaseFinding):
    def __init__(self, tag, txt):
        self.onset = UNINITIALIZED_VAL
        self.offset = UNINITIALIZED_VAL
        super().__init__(tag, txt)

    def decode(self):
        super().decode()
        fill_temporal_util(self, self.finding_txt)


# inherits from base tag, includes frequency specific information
#                       Optional                               Optional       Optional     Optional
# TAG (ANALYSIS_TYPE CORRELATION_SIGN BAND_LOW-BAND_HIGHHz <ONSET-OFFSETms>  <TECHNIQUE>   #COMMENT)
class FrequencyFinding(BaseFinding):
    def __init__(self, tag, txt):
        self.analysis = UNINITIALIZED_VAL
        self.direction = FREQ_DIRECTION_DEF_VAL
        self.band_low = UNINITIALIZED_VAL
        self.band_high = UNINITIALIZED_VAL
        self.onset = UNINITIALIZED_VAL
        self.offset = UNINITIALIZED_VAL
        self.technique = UNINITIALIZED_VAL
        super().__init__(tag, txt)

    def decode(self):
        super().decode()
        # split frequency information
        freq_split = self.finding_txt.replace(
            FINDING_INNER_S_SEP,
            " ",
        ).split(FREQUENCY_DATA_SEP)
        # 1st item - analysis type (obligatory)
        analysis_type = freq_split[0].strip()
        if str(analysis_type).lower() == "power":
            self.analysis = AnalysisTypeChoices.POWER
        elif str(analysis_type).lower() == "connectivity":
            self.analysis = AnalysisTypeChoices.CONNECTIVITY
        elif str(analysis_type).lower() == "phi":
            self.analysis = AnalysisTypeChoices.PHI
        elif str(analysis_type).lower() == "complexity":
            self.analysis = AnalysisTypeChoices.COMPLEXITY
        elif str(analysis_type).lower() == "te":
            self.analysis = AnalysisTypeChoices.TE
        elif str(analysis_type).lower() == "pca":
            self.analysis = AnalysisTypeChoices.PCA
        elif str(analysis_type).lower() == "lrtc":
            self.analysis = AnalysisTypeChoices.LRTC
        elif str(analysis_type).lower() in ["microstates", "microstate"]:
            self.analysis = AnalysisTypeChoices.MICROSTATES
        elif str(analysis_type).lower() == "cd":
            self.analysis = AnalysisTypeChoices.CD
        elif str(analysis_type).lower() == "clustering":
            self.analysis = AnalysisTypeChoices.CLUSTERING
        elif str(analysis_type).lower() == "mst":
            self.analysis = AnalysisTypeChoices.MST
        elif str(analysis_type).lower() == "psd":
            self.analysis = AnalysisTypeChoices.PSD
        elif str(analysis_type).lower() == "ersp":
            self.analysis = AnalysisTypeChoices.ERSP
        else:
            raise FindingTagDataError(f"Parsed analysis type: {analysis_type} not compatible with existing options")

        band_idx = FREQ_BAND_DEF_IDX

        # direction (+/-) is optional, so keep track of the items index
        if FREQ_DIRECTION_NEGATIVE in freq_split:
            self.direction = DirectionChoices.NEGATIVE
            band_idx = band_idx + 1

        # band is obligatory
        re.split(ONSET_OFFSET_SEP + FINDING_INNER_S_SEP, freq_split[band_idx])
        band_split = (
            freq_split[band_idx]
            .replace(
                FREQUENCY_HZ,
                "",
            )
            .split(ONSET_OFFSET_SEP)
        )
        self.band_low = float(band_split[0].replace(",", ""))
        if len(band_split) > 1:
            self.band_high = float(band_split[1].replace(",", ""))
        else:
            self.band_high = self.band_low
        # extract the temporal information (here it is optional, unlike the temporal tag case)
        if FINDING_INNER_S_SEP in self.finding_txt:
            temporal_split = self.finding_txt.rsplit(FINDING_INNER_S_SEP, 1)
            fill_temporal_util(self, temporal_split[1])


# set the mapping between tags and decoders
spatial_to_finding = {
    tag: SpatialFinding for tag in ["0", "1", "2", "11", "12", "16", "17", "21", "31", "35", "42", "51", "86", "87"]
}
temporal_to_finding = {
    tag: TemporalFinding
    for tag in [
        "3",
        "4",
        "15",
        "22",
        "23",
        "25",
        "26",
        "27",
        "30",
        "32",
        "33",
        "36",
        "37",
        "39",
        "46",
        "49",
        "53",
        "55",
        "56",
        "57",
        "62",
        "63",
        "69",
        "70",
        "71",
        "72",
        "74",
        "75",
        "76",
        "77",
        "78",
        "85",
    ]
}
frequency_to_finding = {tag: FrequencyFinding for tag in ["5", "13", "14", "28", "29"]}
tag_to_findings = spatial_to_finding | temporal_to_finding | frequency_to_finding

# map finding tags that indicate a specific area to this area
finding_tag_to_area = {
    "1": "Ventral Stream",
    "2": "V1",
    "11": "A1",
    "12": "Dorsal Stream",
    "17": "DMN",
    "31": "V4",
    "35": "S1",
    "51": "Uncinate Fasciculus",
    "86": "Dorsal Attention Network",
    "87": "Visual Network",
}


# parses findings for a given tag
def parse_findings_per_tag(tag_code, finding_text):
    # each tag text may include different finding, first split the text
    if finding_text != "":
        inner_findings = [finding.strip() for finding in finding_text.split(INNER_ITEM_SEP) if finding.strip() != ""]
    else:
        inner_findings = [finding_text]
    # we map only positive tags to decoders (same decoder regardless of negative/positive finding)
    clean_tag = tag_code.replace(NEGATIVE_TAG, "")
    # differentiate between base tags for which basic parsing is needed and specific decoders
    if clean_tag in tag_to_findings:
        findings = [tag_to_findings[clean_tag](tag_code, finding) for finding in inner_findings]
    else:
        findings = [BaseFinding(tag_code, finding) for finding in inner_findings]

    return findings


# go over an experiment's findings and return a list of findings (here a list of class instances)
def parse(txt):
    # each experiment findings text includes different tags, first split the text
    findings_txt = [tag_txt.strip() for tag_txt in str(txt).split(ITEM_SEP)]
    # in cases where no information is provided for the tag, create mock start and end signs
    findings_txt_processed = [
        finding if (START_FINDING_SEP in finding) else (finding + START_FINDING_SEP + END_FINDING_SEP)
        for finding in findings_txt
    ]

    # map tag codes to the relevant findings text using a list of tuples (tag_code, finding_text)
    # remove the last chat (closing each tag)
    tag_code_to_finding = [
        (tag[0].replace(" ", ""), tag[1].strip()[:-1])
        for tag in (tag.split(START_FINDING_SEP) for tag in findings_txt_processed)
    ]
    # parse the finding texts
    nested_findings = [parse_findings_per_tag(tag, finding) for tag, finding in tag_code_to_finding]
    # flatten the resulting list (there may be multiple tags nested in one X () text
    findings = [finding for findings_list in nested_findings for finding in findings_list]
    return findings


if __name__ == "__main__":
    # a complex example for one experiment
    finding_txt = (
        "5 (Connectivity Neg 90-120Hz <~300-550ms> <EEG> # a comment & "
        "Power 10-20Hz <!10-550ms># another comment) +"
        "   -1 (Inferior_Frontal <fMRI> & Superior_Frontal <EEG>) + "
        "-2 (FFA    <MEG>) + 11 + 2 (FFA  <fMRI>) + 20 (# not indicating an area if OK)+"
        "2 (Posterior    <fMRI>) + 6 (Dimension of activation) + "
        "14 (Connectivity Neg 7-13Hz <MEG>) + 3 (100-200ms <EEG>) + 4 (!50-!20 <EEG>)"
    )
    parse(finding_txt)
