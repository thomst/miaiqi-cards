from django import forms
from django.contrib import admin
from simple_page.models import Page
from simple_page.models import Section
from . import models


class ThemeInline(admin.TabularInline):
    model = models.WelcomeTheme
    extra = 1


class WelcomeSectionForm(forms.ModelForm):
    class Meta:
        model = models.WelcomeSection
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if we are editing an existing object (self.instance.pk exists)
        if self.instance and self.instance.pk:
            page = self.instance.pages.first()
        else:
            page = Page.objects.first()

        if page:
            sections = page.resolved_obj.main.all()
        else:
            sections = Section.objects.all()

        self.fields["title_nav"].queryset = sections
        self.fields["postcard_nav"].queryset = sections
        self.fields["subtitle_nav"].queryset = sections


@admin.register(models.WelcomeSection)
class WelcomeSection(admin.ModelAdmin):
    form = WelcomeSectionForm
    list_display = ['title']
    search_fields = ['title']
    inlines = [ThemeInline]
