from django.contrib import admin
from . import models


class ThemeInline(admin.TabularInline):
    model = models.WelcomeTheme
    extra = 1


@admin.register(models.WelcomeSection)
class WelcomeSection(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    inlines = [ThemeInline]
