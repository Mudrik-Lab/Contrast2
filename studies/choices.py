from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class SampleChoices(TextChoices):
    HEALTHY_ADULTS = "healthy_adults", _("Healthy_adults")
    CHILDREN = "children", _("Children")
    PATIENTS = "patients", _("Patients")
    NON_HUMAN = "non_human", _("Non_human")
    COMPUTER = "computer", _("Computer")


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
    BOTH = "both", _("Both")


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
