from django.db import models
from django.conf import settings


class Link(models.Model):
    objects = models.Manager()
    url = models.URLField()
    description = models.TextField(blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name="links"
    )


class Vote(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    link = models.ForeignKey(
        Link,
        null=True,
        on_delete=models.CASCADE,
        related_name="votes",
    )
