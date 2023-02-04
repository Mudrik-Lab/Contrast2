from django.db.models import TextChoices, IntegerChoices
from django.utils.translation import gettext_lazy as _


class SampleChoices(TextChoices):
    HEALTHY_ADULTS = "healthy_adults", _("Healthy_adults")
    CHILDREN = "children", _("Children")
    PATIENTS = "patients", _("Patients")
    NON_HUMAN = "non_human", _("Non_human")
    COMPUTER = "computer", _("Computer")


class InterpretationsChoices(TextChoices):
    PRO = "pro", _("Pro"), 1
    CHALLENGES = "challenges", _("Challenges"), 0
    NEUTRAL = "neutral", _("Neutral"), "X"


class TypeOfConsciousnessChoices(TextChoices):
    CONTENT = "content", _("Content"), 1
    STATE = "state", _("State"), 0
    BOTH = "both", _("Both"), 2


class ReportingChoices(TextChoices):
    REPORT = "report", _("Report"), 1
    NO_REPORT = "no_report", _("No_report"), 0
    BOTH = "both", _("Both"), 2


class TheoryDrivenChoices(TextChoices):
    DRIVEN = "driven", _("Driven"), 2
    MENTIONING = "mentioning", _("Mentioning"), 1
    POST_HOC = "post-hoc", _("Post hoc"), 0


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
