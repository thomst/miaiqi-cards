import os

from django.utils.functional import cached_property
from miaiqi_cards.settings import MEDIA_ROOT
from miaiqi_cards.responsive_image.models import Image


class ImagePathsMixin:
    IMAGE_FIELDS = [
        'original',
        'large',
        'medium',
        'small',
    ]

    @cached_property
    def db_files(self):
        files = []
        for image in Image.objects.all():
            for field_name in self.IMAGE_FIELDS:
                file_field = getattr(image, field_name)
                files.append(file_field.path)
        return files

    @cached_property
    def stored_files(self):
        stored = []
        root_path = MEDIA_ROOT / Image.UPLOAD_DIR
        for root, _, files in os.walk(root_path):
            for file in files:
                stored.append(os.path.join(root, file))
        return stored

    @cached_property
    def missing_files(self):
        return [path for path in self.db_files if not os.path.exists(path)]

    @cached_property
    def existing_files(self):
        return [path for path in self.db_files if os.path.exists(path)]

    @cached_property
    def leftover_files(self):
        return [path for path in self.stored_files if path not in self.db_files]
