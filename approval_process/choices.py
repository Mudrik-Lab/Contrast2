from django.db import models


class ApprovalChoices(models.IntegerChoices):
    PENDING = 0
    IN_PROCESS = 3
    APPROVED = 1
    REJECTED = 2
