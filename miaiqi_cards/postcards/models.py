import os
import hashlib
import PIL
from io import BytesIO
from django.db import models
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from reorder_items_widget import ReorderItemsField
from simple_page.models import Section
from ..website.models import SectionMixin


class Resizer:
    SIZES = dict(
        large=(1200, 1200),
        medium=(800, 800),
        small=(400, 400),
    )

    def __init__(self, original):
        self.original = original

    def resize(self, size):
        img = PIL.Image.open(self.original)
        resized = img.resize(self.SIZES[size], PIL.Image.Resampling.LANCZOS)
        avif_data = BytesIO()
        resized.save(avif_data, format='AVIF')
        filename = f'{os.path.splitext(self.original.name)[0]}_{size}.avif'
        avif_data.seek(0)
        return SimpleUploadedFile(filename, avif_data.read(), 'image/avif')


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, *args, **kwargs):
        if self.exists(name):
            self.delete(name)
        return name


def upload_to(instance, filename, fieldname):
    ext = os.path.splitext(filename)[1]
    hash = hashlib.md5(getattr(instance, fieldname).read()).hexdigest()
    new_filename = f"{instance.name}_{fieldname}_{hash}{ext}"
    return os.path.join(Image.UPLOAD_DIR, new_filename)


# Value for upload_to must be serializable, so we define separate functions for
# each field instead of using an UploadTo class with a __call__ method.
def upload_original(*args): return upload_to(*args, 'original')
def upload_large(*args): return upload_to(*args, 'large')
def upload_medium(*args): return upload_to(*args, 'medium')
def upload_small(*args): return upload_to(*args, 'small')


class Image(models.Model):
    UPLOAD_DIR = 'postcards/'

    name = models.CharField(max_length=100, blank=True, unique=True)
    original = models.ImageField(upload_to=upload_original, storage=OverwriteStorage())
    large = models.ImageField(upload_to=upload_large, storage=OverwriteStorage())
    medium = models.ImageField(upload_to=upload_medium, storage=OverwriteStorage())
    small = models.ImageField(upload_to=upload_small, storage=OverwriteStorage())

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.splitext(self.original.name)[0]
        resizer = Resizer(self.original)
        self.large = resizer.resize('large')
        self.medium = resizer.resize('medium')
        self.small = resizer.resize('small')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def srcset(self):
        return f'{self.large.url} {self.large.width}w, {self.medium.url} {self.medium.width}w, {self.small.url} {self.small.width}w'


class Postcard(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, blank=True, related_name='postcard')
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('postcard', kwargs=dict(postcard_id=self.pk))

    class Meta:
        db_table = 'website_postcard'


class GallerySection(SectionMixin, Section):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    postcards = models.ManyToManyField(
        'postcards.Postcard',
        through='GalleryPostcard',
        related_name='galleries',
    )


class GalleryPostcard(models.Model):
    gallery = models.ForeignKey(GallerySection, on_delete=models.CASCADE)
    postcard = models.ForeignKey(Postcard, on_delete=models.CASCADE)
    index = ReorderItemsField()

    class Meta:
        unique_together = ('gallery', 'postcard')
