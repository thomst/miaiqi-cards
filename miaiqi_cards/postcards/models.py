from django.db import models
from django.urls import reverse
from reorder_items_widget import ReorderItemsField
from simple_page.models import Page, Section


class GalleryPage:
    REGIONS = [
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]
    def __init__(self):
        self.title = None
        self.description = None
        self.homepage = Page.objects.first().resolved_obj


class PostcardPage(GalleryPage):
    pass


class Postcard(models.Model):
    title = models.CharField(max_length=200, blank=True, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, related_name='postcard')
    is_public = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.title:
            title = self.image.name.replace('_', ' ').replace('-', ' ')
            self.title = title.capitalize()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        gallery = GallerySection.objects.first()
        return reverse('postcard', kwargs=dict(slug=gallery.slug, postcard_id=self.id))

    class Meta:
        ordering = ['gallerypostcard__index']


class GalleryPostcard(models.Model):
    gallery = models.ForeignKey('GallerySection', on_delete=models.CASCADE)
    postcard = models.ForeignKey(Postcard, on_delete=models.CASCADE)
    index = ReorderItemsField()

    class Meta:
        unique_together = ('gallery', 'postcard')


class GallerySection(Section):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    postcards = models.ManyToManyField(
        Postcard,
        through=GalleryPostcard,
        related_name='galleries',
    )

    def __str__(self):
        return self.title


# class GalleryPostcardSet(models.Model):
#     set_gallery = models.ForeignKey('SetGallerySection', on_delete=models.CASCADE)
#     postcard_set = models.ForeignKey(GallerySection, on_delete=models.CASCADE)
#     index = ReorderItemsField()

#     class Meta:
#         unique_together = ('set_gallery', 'postcard_set')


# class SetGallerySection(Section):
#     title = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     postcard_sets = models.ManyToManyField(
#         GallerySection,
#         through=GalleryPostcardSet,
#         related_name='set_galleries',
#     )

#     def __str__(self):
#         return self.title