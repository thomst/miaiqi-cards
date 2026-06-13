from django.db import models
from django.urls import reverse


class Postcard(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='postcards/')
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        gallery = self.galleries.first()
        if gallery:
            return reverse('postcard', kwargs={'gallery_id': gallery.pk, 'postcard_id': self.pk})
        return '#'

    class Meta:
        db_table = 'website_postcard'
