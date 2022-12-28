from django.db import models


class ApprovalChoices(models.IntegerChoices):
    PENDING = 0
    APPROVED = 1
    REJECTED = 2
