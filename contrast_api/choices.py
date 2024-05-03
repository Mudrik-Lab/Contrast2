from django.db.models import TextChoices, IntegerChoices
from django.utils.translation import gettext_lazy as _


class SampleChoices(TextChoices):
    HEALTHY_ADULTS = "healthy_adults", _("Healthy_adults")
    HEALTHY_COLLEGE_STUDENTS = "Healthy_college_students", _("Healthy_college_students")
    CHILDREN = "children", _("Children")
    PATIENTS = "patients", _("Patients")
    NON_HUMAN = "non_human", _("Non_human")
    COMPUTER = "computer", _("Computer")
    YOUNG_PATIENTS = "Young_patients_(children)", _("Young_patients_(children)")


class UnConSampleChoices(TextChoices):
    HEALTHY_ADULTS = "healthy_adults", _("Healthy adults")
    HEALTHY_COLLEGE_STUDENTS = "Healthy_college_students", _("Healthy college students")
    CHILDREN = "children", _("Children")
    PATIENTS_ADULTS = "patients_adults", _("Patients (adults)")
    PATIENTS_CHILDREN = "patients_children", _("Patients (children)")
    NON_HUMAN = "non_human", _("Non-human")
    COMPUTER = "computer", _("Computer")


class PresentationModeChoices(TextChoices):
    LIMINAL = "liminal", _("Liminal")
    SUBLIMINAL = "subliminal", _("Subliminal")


class InterpretationsChoices(TextChoices):
    PRO = "pro", _("Pro")
    CHALLENGES = "challenges", _("Challenges")
    NEUTRAL = "neutral", _("Neutral")


class AggregatedInterpretationsChoices(TextChoices):
    PRO = "pro", _("Pro")
    CHALLENGES = "challenges", _("Challenges")


class TypeOfConsciousnessChoices(TextChoices):
    CONTENT = "content", _("Content")
    STATE = "state", _("State")
    BOTH = "both", _("Both")


class ReportingChoices(TextChoices):
    REPORT = "report", _("Report")
    NO_REPORT = "no_report", _("No_report")
    BOTH = "both", _("Both")


class TheoryDrivenChoices(TextChoices):
    DRIVEN = "driven", _("Driven")
    MENTIONING = "mentioning", _("Mentioning")
    POST_HOC = "post-hoc", _("Post hoc")


class DirectionChoices(TextChoices):
    NEGATIVE = "negative", _("Negative")
    POSITIVE = "positive", _("Positive")


class AnalysisTypeChoices(TextChoices):
    POWER = "power", _("Power")
    CONNECTIVITY = "connectivity", _("Connectivity")
    PHI = "phi", _("Phi")
    COMPLEXITY = "complexity", _("Complexity")
    TE = "te", _("Te - transfer entropy")
    PCA = "pca", _("PCA - principal components analysis")
    LRTC = "lrtc", _("LRTC - long-range temporal correlations")
    MICROSTATES = "microstates", _("Microstates")
    CD = "cd", _("CD - correlation dimension")
    CLUSTERING = "clustering", _("Clustering")
    MST = "mst", _("MST - minimum spanning tree")
    PSD = "psd", _("PSD - power spectral density")
    ERSP = "ersp", _("ERSP - event-related spectral perturbations")


class ExperimentTypeChoices(IntegerChoices):
    NEUROSCIENTIFIC = 1
    BEHAVIORAL = 2
    BOTH = 3


class AALAtlasTagChoices(TextChoices):
    PRECENTRAL = "Precentral", _("Precentral")
    FRONTAL_SUP = "Frontal_Sup", _("Frontal_Sup")
    FRONTAL_MID = "Frontal_Mid", _("Frontal_Mid")
    FRONTAL_INF_OPER = "Frontal_Inf_Oper", _("Frontal_Inf_Oper")
    FRONTAL_INF_TRI = "Frontal_Inf_Tri", _("Frontal_Inf_Tri")
    FRONTAL_INF_ORB = "Frontal_Inf_Orb", _("Frontal_Inf_Orb")
    ROLANDIC_OPER = "Rolandic_Oper", _("Rolandic_Oper")
    SUPP_MOTOR_AREA = "Supp_Motor_Area", _("Supp_Motor_Area")
    OLFACTORY = "Olfactory", _("Olfactory")
    FRONTAL_SUP_MED = "Frontal_Sup_Med", _("Frontal_Sup_Med")
    FRONTAL_MED_ORB = "Frontal_Med_Orb", _("Frontal_Med_Orb")
    RECTUS = "Rectus", _("Rectus")
    OFCMED = "OFCmed", _("OFCmed")
    OFCANT = "OFCant", _("OFCant")
    OFCPOST = "OFCpost", _("OFCpost")
    OFCLAT = "OFClat", _("OFClat")
    INSULA = "Insula", _("Insula")
    CINGULATE_ANT = "Cingulate_Ant", _("Cingulate_Ant")
    CINGULATE_MID = "Cingulate_Mid", _("Cingulate_Mid")
    CINGULATE_POST = "Cingulate_Post", _("Cingulate_Post")
    HIPPOCAMPUS = "Hippocampus", _("Hippocampus")
    PARAHIPPOCAMPAL = "ParaHippocampal", _("ParaHippocampal")
    AMYGDALA = "Amygdala", _("Amygdala")
    CALCARINE = "Calcarine", _("Calcarine")
    CUNEUS = "Cuneus", _("Cuneus")
    LINGUAL = "Lingual", _("Lingual")
    OCCIPITAL_SUP = "Occipital_Sup", _("Occipital_Sup")
    OCCIPITAL_MID = "Occipital_Mid", _("Occipital_Mid")
    OCCIPITAL_INF = "Occipital_Inf", _("Occipital_Inf")
    FUSIFORM = "Fusiform", _("Fusiform")
    POSTCENTRAL = "Postcentral", _("Postcentral")
    PARIETAL_SUP = "Parietal_Sup", _("Parietal_Sup")
    PARIETAL_INF = "Parietal_Inf", _("Parietal_Inf")
    SUPRAMARGINAL = "SupraMarginal", _("SupraMarginal")
    ANGULAR = "Angular", _("Angular")
    PRECUNEUS = "Precuneus", _("Precuneus")
    PARACENTRAL_LOBULE = "Paracentral_Lobule", _("Paracentral_Lobule")
    CAUDATE = "Caudate", _("Caudate")
    PUTAMEN = "Putamen", _("Putamen")
    PALLIDUM = "Pallidum", _("Pallidum")
    THALAMUS = "Thalamus", _("Thalamus")
    HESCHL = "Heschl", _("Heschl")
    TEMPORAL_SUP = "Temporal_Sup", _("Temporal_Sup")
    TEMPORAL_POLE_SUP = "Temporal_Pole_Sup", _("Temporal_Pole_Sup")
    TEMPORAL_MID = "Temporal_Mid", _("Temporal_Mid")
    TEMPORAL_POLE_MID = "Temporal_Pole_Mid", _("Temporal_Pole_Mid")
    TEMPORAL_INF = "Temporal_Inf", _("Temporal_Inf")
    THAL_AV = "Thal_AV", _("Thal_AV")
    THAL_LP = "Thal_LP", _("Thal_LP")
    THAL_VA = "Thal_VA", _("Thal_VA")
    THAL_VL = "Thal_VL", _("Thal_VL")
    THAL_VPL = "Thal_VPL", _("Thal_VPL")
    THAL_IL = "Thal_IL", _("Thal_IL")
    THAL_RE = "Thal_RE", _("Thal_RE")
    THAL_MDM = "Thal_MDm", _("Thal_MDm")
    THAL_MDL = "Thal_MDl", _("Thal_MDl")
    THAL_LGN = "Thal_LGN", _("Thal_LGN")
    THAL_MGN = "Thal_MGN", _("Thal_MGN")
    THAL_PUA = "Thal_PuA", _("Thal_PuA")
    THAL_PUM = "Thal_PuM", _("Thal_PuM")
    THAL_PUL = "Thal_PuL", _("Thal_PuL")
    THAL_PUI = "Thal_PuI", _("Thal_PuI")
    NOT_SPECIFIED = "Not Specified", _("Not specified")


class StudyTypeChoices(TextChoices):
    CONSCIOUSNESS = _("Consciousness")
    UNCONSCIOUSNESS = _("UnConsciousness")

class SignificanceChoices(TextChoices):
    NEGATIVE = "Negative"
    POSITIVE = "Positive"
    MIXED = "Mixed"
