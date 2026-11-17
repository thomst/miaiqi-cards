from django.db import models
from simple_page.models import Section


class ContactSection(Section):
    title = models.CharField(max_length=100)
    text = models.TextField(blank=True)
    confirmation_text = models.TextField(blank=True)

    def __str__(self):
        return self.title
