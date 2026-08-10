from simple_page.models import Section
from colorfield.fields import ColorField
from django.db import models


class WelcomeSection(Section):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    title_ref = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL, related_name='welcome_title')
    subtitle_ref = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL, related_name='welcome_subtitle')
    postcard_ref = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL, related_name='welcome_postcard')

    def __str__(self):
        return self.title


class WelcomeTheme(models.Model):
    name = models.CharField(max_length=255, blank=True)
    section = models.ForeignKey(WelcomeSection, null=True, on_delete=models.SET_NULL, related_name='themes')
    postcard = models.OneToOneField('postcards.Postcard', on_delete=models.CASCADE)
    h1_color = ColorField(format='hex')
    h1_bg_color = ColorField(format='hex')
    h2_bg_color = ColorField(format='hex')
    img_bg_color = ColorField(format='hex')

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.postcard.title
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Theme: {self.name}'
