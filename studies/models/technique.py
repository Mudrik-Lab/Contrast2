from django.db import models


class Technique(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)

    """
    Ca2 Imaging
    Computational Modelling
    EEG
    fMRI
    Intracranial EEG
    Intracranial Stimulation
    MEG
    MRI
    PET
    tACS
    tDCS
    TMS
    """