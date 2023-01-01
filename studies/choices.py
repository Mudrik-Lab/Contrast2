from django.db.models import TextChoices


class SampleChoices(TextChoices):
    HEALTHY_ADULTS = "healthy_adults"
    CHILDREN = "children"
    PATIENTS = "patients"
    NON_HUMAN = "non_human"
    COMPUTER = "computer"


class InterpretationsChoices(TextChoices):
    PRO = "pro"
    CHALLENGES = "challenges"
    NEUTRAL = "neutral"


class TypeOfConsciousnessChoices(TextChoices):
    CONTENT = "content"
    STATE = "state"
    BOTH = "both"


class ReportingChoices(TextChoices):
    REPORT = "report"
    NO_REPORT = "no_report"
    BOTH = "both"


class TheoryDrivenChoices(TextChoices):
    DRIVEN = "driven"
    MENTIONING = "mentioning"
    BOTH = "both"


class AnalysisTypeChoices(TextChoices):
    NEGATIVE = "negative"
    POSITIVE = "positive"
