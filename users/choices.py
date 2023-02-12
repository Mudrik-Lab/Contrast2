from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class GenderChoices(TextChoices):
    MAN = "man"
    WOMAN = "woman"
    OTHER = "other"
    NOT_REPORTING = "not_reporting"


class AcademicStageChoices(TextChoices):
    UNDERGRADUATE = "undergraduate_student", _("Undergraduate student")
    GRADUATE = "graduate_student", _("Graduate student")
    POSTDOC = "postdoctoral_fellow", _("Postdoctoral fellow")
    PRINCIPLE_RESEARCHER = "principle_researcher", _("Principle researcher")
    OTHER = "other", _("Other")