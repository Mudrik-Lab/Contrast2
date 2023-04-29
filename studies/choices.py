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


class InterpretationsChoices(TextChoices):
    PRO = "pro", _("Pro")
    CHALLENGES = "challenges", _("Challenges")
    NEUTRAL = "neutral", _("Neutral")


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


class CorrelationSignChoices(TextChoices):
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


class ExperimentTypeChoices(IntegerChoices):
    NEUROSCIENTIFIC = 1
    BEHAVIORAL = 2
    BOTH = 3
