from django.db import models
from django.urls import reverse
from reorder_items_widget import ReorderItemsField
from simple_page.models import Page, Section
from miaiqi_cards.responsive_image.models import Image


class PostcardSetPage:
    REGIONS = [
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]
    def __init__(self):
        self.title = None
        self.description = None
        self.homepage = Page.objects.first().resolved_obj


class PostcardPage(PostcardSetPage):
    pass


class Postcard(models.Model):
    title = models.CharField(max_length=200, blank=True, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, related_name='postcard')
    is_public = models.BooleanField(default=True)
    index = ReorderItemsField()

    def save(self, *args, **kwargs):
        if not self.title:
            title = self.image.name.replace('_', ' ').replace('-', ' ')
            self.title = title.capitalize()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        gallery = GallerySection.objects.first()
        kwargs = dict(gallery_slug=gallery.slug, postcard_id=self.id)
        return reverse('postcard', kwargs=kwargs)

    class Meta:
        ordering = ['index']


class PostcardSetPostcard(models.Model):
    postcard_set = models.ForeignKey('PostcardSet', on_delete=models.CASCADE)
    postcard = models.ForeignKey(Postcard, on_delete=models.CASCADE)
    index = ReorderItemsField()

    class Meta:
        unique_together = ('postcard_set', 'postcard')


class PostcardSet(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    index = ReorderItemsField()
    postcards = models.ManyToManyField(
        Postcard,
        through=PostcardSetPostcard,
        related_name='postcard_sets',
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['index']


class GallerySection(Section):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    @property
    def postcards(self):
        return Postcard.objects.all()

    def __str__(self):
        return self.title


class SetsSection(Section):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)


    @property
    def postcard_sets(self):
        return PostcardSet.objects.all()

    def __str__(self):
        return self.title
