# (c) Crown Owned Copyright, 2016. Dstl.
# apps/teams/models.py
from django.core.urlresolvers import reverse
from django.db import models
from apps.organisations.models import Organisation


class Team(models.Model):
    name = models.CharField(max_length=256, unique=True)
    organisation = models.ForeignKey(Organisation)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse('team-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
