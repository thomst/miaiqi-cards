import os
import hashlib
import PIL
import mimetypes
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

    def get_filename(self, size):
        name, ext = os.path.splitext(self.original.name)
        return f'{name}_{size}{ext}'

    def get_content_type(self):
        try:
            return self.original.file.content_type
        except AttributeError:
            return mimetypes.guess_type(self.original.path)[0]

    def resize(self, size):
        img = PIL.Image.open(self.original)
        resized = img.resize(self.SIZES[size], PIL.Image.Resampling.LANCZOS)
        output = BytesIO()
        resized.save(output, format=img.format)
        filename = self.get_filename(size)
        output.seek(0)
        return SimpleUploadedFile(filename, output.read(), self.get_content_type())

    def get_large(self):
        return self.resize('large')

    def get_medium(self):
        return self.resize('medium')

    def get_small(self):
        return self.resize('small')


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, *args, **kwargs):
        if self.exists(name):
            self.delete(name)
        return name


def upload_to(instance, fieldname, filename):
    ext = os.path.splitext(filename)[1]
    hash = hashlib.md5(getattr(instance, fieldname).read()).hexdigest()
    new_filename = f"{instance.name}_{fieldname}_{hash}{ext}"
    return os.path.join(Image.UPLOAD_DIR, new_filename)


def upload_original(instance, filename):
    return upload_to(instance, 'original', filename)


def upload_large(instance, filename):
    return upload_to(instance, 'large', filename)


def upload_medium(instance, filename):
    return upload_to(instance, 'medium', filename)


def upload_small(instance, filename):
    return upload_to(instance, 'small', filename)


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
        self.large = resizer.get_large()
        self.medium = resizer.get_medium()
        self.small = resizer.get_small()
        super().save(*args, **kwargs)


class Postcard(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='postcards/')
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
