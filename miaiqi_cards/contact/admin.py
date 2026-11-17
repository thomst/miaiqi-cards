from django.contrib import admin
from . import models


@admin.register(models.ContactSection)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
