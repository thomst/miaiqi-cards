from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Postcard


@admin.register(Postcard)
class PostcardAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_public', 'view_link']
    search_fields = ['title']

    def view_link(self, obj):
        url = reverse('postcard', kwargs=dict(postcard_id=obj.pk))
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Show</a>', url)
    view_link.short_description = 'Show'
