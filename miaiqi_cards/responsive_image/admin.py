from django.contrib import admin
from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'original', 'large', 'medium', 'small']
    exclude = ['large', 'medium', 'small']
